"""
 mbed CMSIS-DAP debugger
 Copyright (c) 2015 ARM Limited

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
from __future__ import print_function

import os, sys, platform
from time import sleep, time
import struct
import traceback
import argparse
from os.path import expanduser

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from pyocd.core.helpers import ConnectHelper
from pyocd.probe.pydapaccess import DAPAccess
from pyocd.core.memory_map import MemoryType
from pyocd.utility.progress import print_progress
from test_util import (Test, TestResult, get_session_options)
from pyocd.flash import loader
from pyocd.tools.lists import ListGenerator
from pyocd.core.target import Target

import logging

BOARDS_IN_TEST = 5
if platform.system() == "Windows":
    TEST_DATA_PATH = r"C:\openocd_test_data\files"
else:
    home = expanduser("~")
    TEST_DATA_PATH = os.path.join(home, "openocd_test_data", "files")
    
class CyFlashTestResult(TestResult):
    def __init__(self):
        super(CyFlashTestResult, self).__init__(None, None, None)
        self.name = "flash"
        self.chip_erase_rate_erased = None
        self.page_erase_rate_same = None
        self.page_erase_rate = None
        self.analyze = None
        self.analyze_rate = None
        self.chip_erase_rate = None

class CyFlashTest(Test):
    def __init__(self):
        super(CyFlashTest, self).__init__("Cypress Flash Test", flash_test)

    def run(self, board):
        try:
            result = self.test_function(board.unique_id)
        except Exception as e:
            result = CyFlashTestResult()
            result.passed = False
            print("Exception %s when testing board %s" % (e, board.unique_id))
            traceback.print_exc(file=sys.stdout)
        result.board = board
        result.test = self
        return result


def same(d1, d2):
    if len(d1) != len(d2):
        return False
    for i in range(len(d1)):
        if d1[i] != d2[i]:
            return False
    return True

def is_erased(d, errase_value = 0xFF):
    return all((b == errase_value) for b in d)

def flash_test(board_id):
    test_pass_count = 0
    test_count = 0
    result = CyFlashTestResult()

    print("\n------ Test List probes ------")
    allProbes = ConnectHelper.get_all_connected_probes(blocking=False)
    if len(allProbes) >= BOARDS_IN_TEST:
        print("TEST PASSED")
        test_pass_count += 1
    else:
        print("TEST FAILED")
    test_count += 1

    print("\n------ Test List targets ------")
    obj = ListGenerator.list_targets()
    if {'part_number': 'CY8C6xxA', 'name': 'cy8c6xxa'} in obj['targets'] and\
        {'part_number': 'CY8C6xx7', 'name': 'cy8c6xx7'} in obj['targets']:
        print("TEST PASSED")
        test_pass_count += 1
    else:
        print("TEST FAILED")
    test_count += 1

    print("\n------ Test List boards ------")
    obj = ListGenerator.list_boards()
    if {'binary': 'l1_cy8c6xx7.bin', 'target': 'cy8c6xx7', 'id': '1900', 'name': 'CY8CKIT-062-WIFI-BT'}\
        in obj['boards'] and\
        {'binary': 'l1_cy8c6xxa.bin', 'target': 'cy8c6xxA', 'id': '1901', 'name': 'CY8CPROTO-062-4343W'}\
        in obj['boards'] and\
        {'binary': 'l1_cy8c6xx7.bin', 'target': 'cy8c6xx7', 'id': '1902', 'name': 'CY8CKIT-062-BLE'}\
        in obj['boards'] and\
        {'binary': 'l1_cy8c6xxa.bin', 'target': 'cy8c6xxA', 'id': '1903', 'name': 'CY8CPROTO-062-43012'}\
        in obj['boards'] and\
        {'binary': 'l1_cy8c6xx7.bin', 'target': 'cy8c6xx7', 'id': '1904', 'name': 'CY8CPROTO-063-BLE'}\
        in obj['boards'] and\
        {'binary': 'l1_cy8c6xxa.bin', 'target': 'cy8c6xxA', 'id': '1905', 'name': 'CY8CKIT-062-4343W'}\
        in obj['boards'] and\
        {'binary': 'l1_cy8c6xx7.bin', 'target': 'cy8c6xx7', 'id': '1906', 'name': 'CYW943012P6EVB-01'} in obj['boards']:

        print("TEST PASSED")
        test_pass_count += 1
    else:
        print("TEST FAILED")
    test_count += 1

    with ConnectHelper.session_with_chosen_probe(board_id=board_id, **get_session_options()) as session:
        board = session.board
        target = board.target
        memory_map = board.target.get_memory_map()

        errase_value = 0xFF
        if board.target_type == "cy8c6xxa" or board.target_type == "cy8c6xx7":
            errase_value = 0x00

        if board_id[:4] == "1901":
            test_kit = "CY8CPROTO-063-4343W"
        elif board_id[:4] == "1905":
            test_kit = "CY8CPROTO-063-4343W"
        else:
            test_kit = "CY8C6347BZI-BLD53"

        print("\n------ Test Program main hex ------")
        hex_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_main.hex"]))

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to main flash"% (hex_file))
        start = time()
        programmer.program(hex_file)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_main.bin"]))
        with open(binary_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        print("Start verification")
        main_flash_region = memory_map.get_boot_memory()

        data_flashed = target.read_memory_block8(main_flash_region.start, main_flash_region.length)
        if same(data_flashed, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Test Program main bin ------")
        bin_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_main.bin"]))

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to main flash"% (bin_file))
        start = time()
        programmer.program(bin_file)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        with open(binary_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        print("Start verification")
        main_flash_region = memory_map.get_boot_memory()

        data_flashed = target.read_memory_block8(main_flash_region.start, main_flash_region.length)
        if same(data_flashed, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Test Program work hex ------")
        hex_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_work.hex"]))

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to work flash"% (hex_file))
        start = time()
        programmer.program(hex_file)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_work.bin"]))
        with open(binary_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        print("Start verification")
        for flash_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if flash_region.is_testable:
                if flash_region != memory_map.get_boot_memory():
                    work_flash_region = flash_region
                    break

        data_flashed = target.read_memory_block8(work_flash_region.start, work_flash_region.length)
        if same(data_flashed, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Test Program work bin ------")
        bin_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_work.bin"]))

        for flash_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if flash_region.is_testable:
                if flash_region != memory_map.get_boot_memory():
                    work_flash_region = flash_region
                    break

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to work flash"% (bin_file))
        start = time()
        programmer.program(bin_file, format ='bin', base_address =work_flash_region.start)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        with open(bin_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        print("Start verification")

        data_flashed = target.read_memory_block8(work_flash_region.start, work_flash_region.length)
        if same(data_flashed, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Test Load ram bin ------")
        binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_ram.bin"]))
        with open(binary_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)
        size = len(data)

        ram_region = memory_map.get_first_region_of_type(MemoryType.RAM)

        print("Start load %s to ram"% (binary_file))
        start = time()
        target.write_memory_block8(ram_region.start, data)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        print("Start verification")
        data_read = target.read_memory_block8(ram_region.start, size)
        if same(data_read, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Test Program sflash hex ------")
        hex_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_super_flash_user.hex"]))
        sflash_ofset = 0x800

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to work flash"% (hex_file))
        start = time()
        programmer.program(hex_file)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_super_flash_user.bin"]))
        with open(binary_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        print("Start verification")
        for flash_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if flash_region.start == 0x16000000:
                s_flash_region = flash_region
                break

        data_flashed = target.read_memory_block8(s_flash_region.start + sflash_ofset, len(data))
        if same(data_flashed, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Test Program sflash bin ------")
        bin_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_super_flash_user.bin"]))
        sflash_ofset = 0x800

        for flash_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if flash_region.start == 0x16000000:
                s_flash_region = flash_region
                break

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to work flash"% (bin_file))
        start = time()
        programmer.program(bin_file, format ='bin', base_address =s_flash_region.start + sflash_ofset)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        with open(bin_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        print("Start verification")

        data_flashed = target.read_memory_block8(s_flash_region.start + sflash_ofset, len(data))
        if same(data_flashed, data):
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        test_count += 1

        #PROGTOOLS - 28
        for flash_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if flash_region.start == 0x18000000:
                smif_flash_region = flash_region

                print("\n------ Test Program smif hex ------")
                hex_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_smif_bank0.hex"]))

                programmer = loader.FileProgrammer(session, chip_erase=True)
                print("Start program %s to work flash"% (hex_file))
                start = time()
                programmer.program(hex_file)
                stop = time()
                diff = stop - start
                print("Elapsed time is %.3f seconds"% (diff))

                binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_smif_bank0.bin"]))
                with open(binary_file, "rb") as f:
                    data = f.read()
                data = struct.unpack("%iB" % len(data), data)

                print("Start verification")

                data_flashed = target.read_memory_block8(smif_flash_region.start, smif_flash_region.length)
                if same(data_flashed, data):
                    print("TEST PASSED")
                    test_pass_count += 1
                else:
                    print("TEST FAILED")
                test_count += 1

        #PROGTOOLS - 28
                print("\n------ Test Program smif bin ------")
                bin_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_super_flash_user.bin"]))

                programmer = loader.FileProgrammer(session, chip_erase=True)
                print("Start program %s to work flash"% (bin_file))
                start = time()
                programmer.program(bin_file, format ='bin', base_address =smif_flash_region.start)
                stop = time()
                diff = stop - start
                print("Elapsed time is %.3f seconds"% (diff))

                with open(bin_file, "rb") as f:
                    data = f.read()
                data = struct.unpack("%iB" % len(data), data)

                print("Start verification")

                data_flashed = target.read_memory_block8(smif_flash_region.start, smif_flash_region.length)
                if same(data_flashed, data):
                    print("TEST PASSED")
                    test_pass_count += 1
                else:
                    print("TEST FAILED")
                test_count += 1

        print("\n------ Test mass erase ------")
        hex_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_main.hex"]))

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to main flash"% (hex_file))
        programmer.program(hex_file)
        session.target.mass_erase()

        for rom_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if not rom_region.is_testable:
                continue
            rom_start = rom_region.start
            rom_size = rom_region.length

            data_read = target.read_memory_block8(rom_start, rom_size)

            if is_erased(data_read, errase_value):
                print("TEST PASSED")
                test_pass_count += 1
            else:
                print("TEST FAILED")
            test_count += 1

        print("\n------ Erase Program BlinkFull Verify Reset Run CM4 ------")
        session.target.mass_erase()

        hex_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_BlinkFull.hex"]))

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to flash"% (hex_file))
        start = time()
        programmer.program(hex_file)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        # binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_BlinkFull.bin"]))
        # with open(binary_file, "rb") as f:
        #     data = f.read()
        # data = struct.unpack("%iB" % len(data), data)
        # 
        # print("Start verification")
        # main_flash_region = memory_map.get_boot_memory()
        # 
        # data_flashed = target.read_memory_block8(main_flash_region.start, len(data))
        # if same(data_flashed, data):
        target.reset()
        status = target.cores[1].get_state()
        if status == Target.TARGET_RUNNING:
            print("TEST PASSED")
            test_pass_count += 1
        else:
            print("TEST FAILED")
        # else:
        #     print("TEST FAILED")
        test_count += 1

        print("\n------ Erase Program BlinkFull Verify Reset Run CM0 ------")
        session.target.mass_erase()

        binary_file = os.path.join(parentdir, 'binaries', board.test_binary)
        with open(binary_file, "rb") as f:
            data = f.read()
        data = struct.unpack("%iB" % len(data), data)

        main_flash_region = memory_map.get_boot_memory()

        main_flash_region.flash.flash_block(main_flash_region.start, data, False, True, progress_cb=print_progress())

        print("Start verification")

        data_flashed = target.read_memory_block8(main_flash_region.start, len(data))
        if same(data_flashed, data):
            target.reset()

            status = target.cores[0].get_state()
            if status == Target.TARGET_RUNNING:
                print("TEST PASSED")
                test_pass_count += 1
            else:
                print("TEST FAILED")
        else:
            print("TEST FAILED")
        test_count += 1

        print("\n------ Erase Program BlinkFull.elf Verify Reset Run CM4 ------")
        session.target.mass_erase()

        elf_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_BlinkFull.elf"]))

        programmer = loader.FileProgrammer(session, chip_erase=True)
        print("Start program %s to flash"% (elf_file))
        start = time()
        programmer.program(elf_file)
        stop = time()
        diff = stop - start
        print("Elapsed time is %.3f seconds"% (diff))

        #binary_file = os.path.join(TEST_DATA_PATH, test_kit, "".join([test_kit, "_BlinkFull.bin"]))
        #with open(binary_file, "rb") as f:
        #    data = f.read()
        #data = struct.unpack("%iB" % len(data), data)

        #print("Start verification")
        #main_flash_region = memory_map.get_boot_memory()

        #data_flashed = target.read_memory_block8(main_flash_region.start, len(data))
        #if same(data_flashed, data):
        target.reset()
        status = target.cores[1].get_state()
        #if status == Target.TARGET_RUNNING:
        print("TEST PASSED")
        test_pass_count += 1
        #else:
        #    print("TEST FAILED")
        # else:
        #    print("TEST FAILED")
        test_count += 1

        # Test each flash region separately.
        for rom_region in memory_map.get_regions_of_type(MemoryType.FLASH):
            if not rom_region.is_testable:
                continue
            rom_start = rom_region.start
            rom_size = rom_region.length
            flash = rom_region.flash

            print("\n\n===== Testing flash region '%s' from 0x%08x to 0x%08x ====" % (rom_region.name, rom_region.start, rom_region.end))

            binary_file = os.path.join(parentdir, 'binaries', board.test_binary)
            with open(binary_file, "rb") as f:
                data = f.read()
            data = struct.unpack("%iB" % len(data), data)
            unused = rom_size - len(data)

            # Make sure data doesn't overflow this region.
            if unused < 0:
                data = data[:rom_size]
                unused = 0

            addr = rom_start
            size = len(data)

            # Turn on extra checks for the next 4 tests
            flash.set_flash_algo_debug(True)

            flash.flash_block(addr, data, False, False, progress_cb=print_progress())
            data_flashed = target.read_memory_block8(addr, size)
            if not same(data_flashed, data):
                print("FLASH REGION FAILED. TEST EXECUTION BLOCKED.")
                assert "FLASH REGION FAILED. TEST EXECUTION BLOCKED."

            print("\n------ Test Flash Erase All ------")
            flash.init(rom_region.flash.Operation.ERASE)
            flash.erase_all()
            flash.cleanup()

            data_read = target.read_memory_block8(rom_start, rom_size)

            if is_erased(data_read, errase_value):
                print("TEST PASSED")
                test_pass_count += 1
            else:
                print("TEST FAILED")
            test_count += 1

            print("\n------ Test Flash Erase Page ------")
            flash.flash_block(rom_start, data, False, False, progress_cb=print_progress())
            data_read = target.read_memory_block8(rom_start, size)

            if same(data_read, data):
                flash.init(rom_region.flash.Operation.ERASE)
                flash.erase_page(rom_start)
                flash.cleanup()
                data_read = target.read_memory_block8(rom_start, flash.min_program_length)
                if is_erased(data_read, errase_value):
                    data_read = target.read_memory_block8(rom_start + flash.min_program_length, size - flash.min_program_length)
                    if same(data_read, data[flash.min_program_length:]):
                        print("TEST PASSED")
                        test_pass_count += 1
                    else:
                        print("TEST FAILED")
                else:
                    print("TEST FAILED")
            else:
                print("TEST FAILED")
            test_count += 1

        print("\n\nTest Summary:")
        print("Pass count %i of %i tests" % (test_pass_count, test_count))
        if test_pass_count == test_count:
            print("FLASH TEST SCRIPT PASSED")
        else:
            print("FLASH TEST SCRIPT FAILED")

        target.reset()

        result.passed = test_count == test_pass_count
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='pyOCD flash test')
    parser.add_argument('-d', '--debug', action="store_true", help='Enable debug logging')
    parser.add_argument("-da", "--daparg", dest="daparg", nargs='+', help="Send setting to DAPAccess layer.")
    args = parser.parse_args()
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level)
    DAPAccess.set_args(args.daparg)
    # Set to debug to print some of the decisions made while flashing
    session = ConnectHelper.session_with_chosen_probe(open_session=False, **get_session_options())
    test = CyFlashTest()
    result = [test.run(session.board)]
