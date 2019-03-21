# pyOCD debugger
# Copyright (c) 2013-2019 Arm Limited
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from time import (sleep)

from .CY8C6xx7_MAIN import flash_algo as flash_algo_main
from .CY8C6xx7_WORK import flash_algo as flash_algo_work
from .CY8C64xx_SMIF import flash_algo as flash_algo_smif

from .target_CY8C6xx7 import PSoC6FlashCommon
from ...core import exceptions
from ...core.coresight_target import CoreSightTarget
from ...core.memory_map import (FlashRegion, RamRegion, RomRegion, MemoryMap)
from ...core.target import Target
from ...coresight.cortex_m import CortexM
from ...utility.notification import Notification
from ...utility.timeout import Timeout
from ...flash.flash import Flash

is_flashing = False

class PSoC6FlashSecure(PSoC6FlashCommon):
    def __init__(self, target, flash_algo):
        super(PSoC6FlashSecure, self).__init__(target, flash_algo)
        
    def init(self, operation, address=None, clock=0, reset=True):
        global is_flashing
        is_flashing = True
        super(PSoC6FlashSecure, self).init(operation, address, clock, reset)

    def uninit(self):
        global is_flashing
        super(PSoC6FlashSecure, self).uninit()
        is_flashing = False

class Flash_CY8C64xx_Main(PSoC6FlashSecure):
    def __init__(self, target):
        super(Flash_CY8C64xx_Main, self).__init__(target, flash_algo_main)


class Flash_CY8C64xx_Work(PSoC6FlashSecure):
    def __init__(self, target):
        super(Flash_CY8C64xx_Work, self).__init__(target, flash_algo_work)

        
class Flash_CY8C64xx_SMIF(Flash):
    def __init__(self, target):
        super(Flash_CY8C64xx_SMIF, self).__init__(target, flash_algo_smif)
        
    def init(self, operation, address=None, clock=0, reset=True):
        global is_flashing
        is_flashing = True
        super(Flash_CY8C64xx_SMIF, self).init(operation, address, clock, reset)

    def uninit(self):
        global is_flashing
        super(Flash_CY8C64xx_SMIF, self).uninit()
        is_flashing = False
        
        
class cy8c64xx(CoreSightTarget):
    VENDOR = "Cypress"
    AP_NUM = None

    memoryMap = MemoryMap(
        RomRegion(start=0x00000000, length=0x20000),
        FlashRegion(start=0x10000000, length=0xA0000, blocksize=0x200, is_boot_memory=True, erased_byte_value=0,
                    algo=flash_algo_main, flash_class=Flash_CY8C64xx_Main),
        FlashRegion(start=0x14000000, length=0x8000, blocksize=0x200, is_boot_memory=False, erased_byte_value=0,
                    algo=flash_algo_work, flash_class=Flash_CY8C64xx_Work),
        FlashRegion(start=0x18000000, length=0x1000000, blocksize=0x10000, is_boot_memory=False, erased_byte_value=0xFF,
                    is_testable=False, algo=flash_algo_smif, flash_class=Flash_CY8C64xx_SMIF),
        RamRegion(start=0x08000000, length=0x20000)
    )

    def __init__(self, link, ap_num):
        super(cy8c64xx, self).__init__(link, self.memoryMap)
        self.AP_NUM = ap_num

    def create_init_sequence(self):
        seq = super(cy8c64xx, self).create_init_sequence()
        seq.replace_task('find_aps', self.find_aps)
        seq.replace_task('create_cores', self.create_cy8c6xx7_core)
        return seq

    def find_aps(self):
        if self.dp.valid_aps is not None:
            return

        self.dp.valid_aps = (self.AP_NUM,)

    def create_cy8c6xx7_core(self):
        core = CortexM_CY8C6xx7(self, self.aps[self.AP_NUM], self.memory_map, 0)
        core.default_reset_type = self.ResetType.SW_SYSRESETREQ
        self.aps[self.AP_NUM].core = core
        core.init()
        self.add_core(core)


class cy8c64xx_cm0(cy8c64xx):
    def __init__(self, link):
        super(cy8c64xx_cm0, self).__init__(link, 1)


class cy8c64xx_cm4(cy8c64xx):
    def __init__(self, link):
        super(cy8c64xx_cm4, self).__init__(link, 2)


class CortexM_CY8C6xx7(CortexM):
    def reset(self, reset_type=None):
        self.notify(Notification(event=Target.EVENT_PRE_RESET, source=self))

        self._run_token += 1

        if reset_type is Target.ResetType.HW:
            self.session.probe.reset()
            self.reinit_dap()
            # This is ugly, but FPB gets disabled after HW Reset so breakpoints stop working
            self.bp_manager._fpb.enable()

        else:
            if reset_type is Target.ResetType.SW_VECTRESET:
                mask = CortexM.NVIC_AIRCR_VECTRESET
            else:
                mask = CortexM.NVIC_AIRCR_SYSRESETREQ

            try:
                self.write_memory(CortexM.NVIC_AIRCR, CortexM.NVIC_AIRCR_VECTKEY | mask)
                self.flush()
            except exceptions.TransferError:
                self.flush()

        with Timeout(5.0) as t_o:
            while t_o.check():
                try:
                    self._ap.dp.init()
                    self._ap.dp.power_up_debug()
                    dhcsr_reg = self.read32(CortexM.DHCSR)
                    if (dhcsr_reg & CortexM.S_RESET_ST) == 0:
                        break
                    self.flush()
                except exceptions.TransferError:
                    sleep(0.01)

        self.notify(Notification(event=Target.EVENT_POST_RESET, source=self))

    def wait_halted(self):
        with Timeout(5.0) as t_o:
            while t_o.check():
                try:
                    if not self.is_running():
                        return
                except exceptions.TransferError:
                    self.flush()
                    sleep(0.01)
            else:
                raise Exception("Timeout waiting for target halt")

    def reinit_dap(self):
        with Timeout(2.0) as t_o:
            while t_o.check():
                try:
                    self._ap.dp.init()
                    self._ap.dp.power_up_debug()
                    self.flush()
                    return
                except exceptions.TransferError:
                    self.flush()

            if not t_o.check():
                logging.error("Failed to initialize DAP")
                
    def acquire(self):
        with Timeout(2.0) as t_o:
            while t_o.check():
                try:
                    self._ap.dp.init()
                    self._ap.dp.power_up_debug()
                    self.write32(0x4023004C, 0)
                    self.write32(0x40260100, 0x80000000)
                    self.flush()
                    return
                except exceptions.TransferError:
                    pass
                
            if not t_o.check():
                logging.error("Failed to enter test mode")

    def reset_and_halt(self, reset_type=None):
        logging.info("Acquiring target...")
        
        #self.reset(self.ResetType.SW_SYSRESETREQ)
        self.write_memory(CortexM.NVIC_AIRCR, CortexM.NVIC_AIRCR_VECTKEY | CortexM.NVIC_AIRCR_SYSRESETREQ)
        try:
            self.flush()
        except exceptions.TransferError:
            pass
        
        self.acquire()

        with Timeout(5.0) as t_o:
            while t_o.check():
                try:
                    if self.read32(0x4023004C) == 0x12344321:
                        break
                except exceptions.TransferError:
                    pass

        if not t_o.check():
            logging.error("Failed to acquire the target (listen window not implemented?)")

        if self.ap.ap_num == 2 and self.read32(0x40210080) & 3 != 3:
            logging.warning("CM4 is sleeping, trying to wake it up...")
            self.write32(0x40210080, 0x05fa0003)

        self.halt()
        self.wait_halted()
        self.write_core_register('xpsr', CortexM.XPSR_THUMB)
    
    def resume(self):
        global is_flashing
        if not is_flashing:
            logging.info("Clearing TEST_MODE bit...")
            self.write32(0x40260100, 0x00000000)

        super(CortexM_CY8C6xx7, self).resume()
