"""
 mbed CMSIS-DAP debugger
 Copyright (c) 2006-2019 ARM Limited

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
import logging
from time import (time, sleep)

from ..core import exceptions
from ..core.coresight_target import CoreSightTarget
from ..core.memory_map import (FlashRegion, RamRegion, RomRegion, MemoryMap)
from ..core.target import Target
from ..coresight.cortex_m import CortexM
from ..flash.flash import Flash
from ..utility.notification import Notification

flash_algo_main = {
    'load_address': 0x08000000,

    # Flash algorithm as a hex string
    'instructions': [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x20004603, 0x46014770, 0x47702000, 0xf000b510, 0xbd10f972, 0x4604b510, 0xf0004620, 0xbd10f915,
        0x4606b570, 0x4615460c, 0x46294622, 0xf0004630, 0xbd70f969, 0x4604b570, 0x4616460d, 0x46294632,
        0xf0004620, 0xbd70f81f, 0x47706001, 0x600a6802, 0x21004770, 0x1c49e000, 0x43424ad6, 0xd8fa428a,
        0xb5084770, 0x48d44669, 0xfff0f7ff, 0x0209210f, 0x40089800, 0xd1012800, 0xe0002001, 0x46032000,
        0xbd084618, 0x4603b570, 0x461d460c, 0xe0052100, 0x5c6e5c50, 0xd00042b0, 0x1c49e002, 0xd3f742a1,
        0x1858bf00, 0xb5febd70, 0x460b4605, 0x20004616, 0x24009002, 0x01682700, 0x184049c0, 0xbf009000,
        0x9800a901, 0xf7ff301c, 0x9801ffc1, 0x2b000fc7, 0x2f00d001, 0x2b00d103, 0x2f00d103, 0x2001d101,
        0x2000e000, 0x2c004604, 0x9802d109, 0xd90042b0, 0x2001e007, 0xffadf7ff, 0x1c409802, 0x2c009002,
        0xbf00d0de, 0x21014620, 0xbdfe4048, 0x4604b5f8, 0x2600460d, 0x01602300, 0x184749a8, 0x4669bf00,
        0xf7ff4638, 0x9800ff93, 0x2b000fc3, 0x42aed106, 0xe005d900, 0xf7ff2001, 0x1c76ff8c, 0xd0ee2b00,
        0x4618bf00, 0x40482101, 0xb5f0bdf8, 0x460d4607, 0x26004613, 0xbf002400, 0x46384619, 0xff76f7ff,
        0x0f006818, 0x21050700, 0x42880749, 0x2001d101, 0x2000e000, 0x2c004604, 0x42aed106, 0xe005d900,
        0xf7ff2001, 0x1c76ff66, 0xd0e52c00, 0x4620bf00, 0x40482101, 0xb5f3bdf0, 0x4606b082, 0x48882700,
        0x90014478, 0x0fc007f0, 0x40482101, 0x25009000, 0xff57f7ff, 0xd0022800, 0x4d802400, 0x2401e002,
        0x35204d7e, 0x31f521ff, 0xf7ff4620, 0x4607ff9f, 0xd1362f00, 0x28009800, 0x4628d005, 0x9901300c,
        0xff32f7ff, 0x4631e004, 0x300c4628, 0xff2cf7ff, 0x30104620, 0x40822201, 0x48724611, 0xff24f7ff,
        0x46282101, 0xf7ff3008, 0x22ffff1f, 0x210032f5, 0xf7ff4620, 0x4607ff48, 0xd1122f00, 0x28009800,
        0x21ffd007, 0x9a0331f5, 0xf7ff9801, 0x4607ff8e, 0x21ffe007, 0x462831f5, 0x9a03300c, 0xff85f7ff,
        0x46384607, 0xbdf0b004, 0x4604b538, 0x447d4d5c, 0x495d3dae, 0xf7ff4628, 0x4621fef7, 0xf7ff1d28,
        0x4669fef3, 0xf7ff4858, 0xbd38ff96, 0x4604b538, 0x447d4d53, 0x49553dd2, 0xf7ff4628, 0x4621fee5,
        0xf7ff1d28, 0x4669fee1, 0xf7ff4850, 0xbd38ff84, 0x4604b538, 0x447d4d4a, 0x494c3df6, 0xf7ff4628,
        0x4621fed3, 0xf7ff1d28, 0x4669fecf, 0xf7ff4847, 0xbd38ff72, 0x4c46b518, 0x4946447c, 0xf7ff4620,
        0x4669fec3, 0xf7ff4843, 0xbd18ff66, 0x4606b570, 0x2500460c, 0x4630e00a, 0xffb6f7ff, 0x2d004605,
        0xe005d000, 0x36ff36ff, 0x1e643602, 0xd1f22c00, 0x4628bf00, 0xb510bd70, 0xf7ff2400, 0x4604ffdb,
        0xbd104620, 0x4605b5f8, 0x4617460e, 0x447c4c30, 0x49313c56, 0xf7ff4620, 0x21fffe97, 0x1d203107,
        0xfe92f7ff, 0x46204629, 0xf7ff3008, 0x4631fe8d, 0x300c4620, 0xfe88f7ff, 0x48274669, 0xff2bf7ff,
        0xb5f8bdf8, 0x460e4605, 0x4c214617, 0x3c94447c, 0x46204922, 0xfe78f7ff, 0x310721ff, 0xf7ff1d20,
        0x4629fe73, 0x30084620, 0xfe6ef7ff, 0x46204631, 0xf7ff300c, 0x4669fe69, 0xf7ff4818, 0xbdf8ff0c,
        0xb0ffb570, 0x4605b081, 0x24002600, 0x2000e003, 0x55084669, 0x20011c64, 0x42840240, 0x4602dbf7,
        0x46284669, 0xffcdf7ff, 0x46304606, 0xb001b07f, 0x0000bd70, 0x00000d05, 0x40200000, 0x40220000,
        0x0000023c, 0x40221008, 0x1c000100, 0x14000100, 0x00000124, 0x0a000100, 0x06000100, 0x05000100,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000
    ],

    # Relative function addresses
    'pc_init': 0x08000021,
    'pc_unInit': 0x08000027,
    'pc_program_page': 0x08000041,
    'pc_erase_sector': 0x08000035,
    'pc_eraseAll': 0x0800002d,

    'static_base': 0x08000000 + 0x00000020 + 0x000009f4,
    'begin_stack': 0x08000d00,
    'begin_data': 0x08000000 + 0x1000,
    'page_size': 0x200,
    'analyzer_supported': False,
    'analyzer_address': 0x00000000,
    'page_buffers': [0x08001000, 0x08001200],  # Enable double buffering
    'min_program_length': 0x200,

    # Flash information
    'flash_start': 0x10000000,
    'flash_size': 0x200000,
    'sector_sizes': (
        (0x0, 0x200),
    )
}

flash_algo_work = {
    'load_address': 0x08000000,

    # Flash algorithm as a hex string
    'instructions': [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x20004603, 0x46014770, 0x47702000, 0xf000b510, 0xbd10f972, 0x4604b510, 0xf0004620, 0xbd10f915,
        0x4606b570, 0x4615460c, 0x46294622, 0xf0004630, 0xbd70f96c, 0x4604b570, 0x4616460d, 0x46294632,
        0xf0004620, 0xbd70f81f, 0x47706001, 0x600a6802, 0x21004770, 0x1c49e000, 0x43424ad7, 0xd8fa428a,
        0xb5084770, 0x48d54669, 0xfff0f7ff, 0x0209210f, 0x40089800, 0xd1012800, 0xe0002001, 0x46032000,
        0xbd084618, 0x4603b570, 0x461d460c, 0xe0052100, 0x5c6e5c50, 0xd00042b0, 0x1c49e002, 0xd3f742a1,
        0x1858bf00, 0xb5febd70, 0x460b4605, 0x20004616, 0x24009002, 0x01682700, 0x184049c1, 0xbf009000,
        0x9800a901, 0xf7ff301c, 0x9801ffc1, 0x2b000fc7, 0x2f00d001, 0x2b00d103, 0x2f00d103, 0x2001d101,
        0x2000e000, 0x2c004604, 0x9802d109, 0xd90042b0, 0x2001e007, 0xffadf7ff, 0x1c409802, 0x2c009002,
        0xbf00d0de, 0x21014620, 0xbdfe4048, 0x4604b5f8, 0x2600460d, 0x01602300, 0x184749a9, 0x4669bf00,
        0xf7ff4638, 0x9800ff93, 0x2b000fc3, 0x42aed106, 0xe005d900, 0xf7ff2001, 0x1c76ff8c, 0xd0ee2b00,
        0x4618bf00, 0x40482101, 0xb5f0bdf8, 0x460d4607, 0x26004613, 0xbf002400, 0x46384619, 0xff76f7ff,
        0x0f006818, 0x21050700, 0x42880749, 0x2001d101, 0x2000e000, 0x2c004604, 0x42aed106, 0xe005d900,
        0xf7ff2001, 0x1c76ff66, 0xd0e52c00, 0x4620bf00, 0x40482101, 0xb5f3bdf0, 0x4606b082, 0x48892700,
        0x90014478, 0x0fc007f0, 0x40482101, 0x25009000, 0xff57f7ff, 0xd0022800, 0x4d812400, 0x2401e002,
        0x35204d7f, 0x31f521ff, 0xf7ff4620, 0x4607ff9f, 0xd1362f00, 0x28009800, 0x4628d005, 0x9901300c,
        0xff32f7ff, 0x4631e004, 0x300c4628, 0xff2cf7ff, 0x30104620, 0x40822201, 0x48734611, 0xff24f7ff,
        0x46282101, 0xf7ff3008, 0x22ffff1f, 0x210032f5, 0xf7ff4620, 0x4607ff48, 0xd1122f00, 0x28009800,
        0x21ffd007, 0x9a0331f5, 0xf7ff9801, 0x4607ff8e, 0x21ffe007, 0x462831f5, 0x9a03300c, 0xff85f7ff,
        0x46384607, 0xbdf0b004, 0x4604b538, 0x447d4d5d, 0x495e3dae, 0xf7ff4628, 0x4621fef7, 0xf7ff1d28,
        0x4669fef3, 0xf7ff4859, 0xbd38ff96, 0x4604b538, 0x447d4d54, 0x49563dd2, 0xf7ff4628, 0x4621fee5,
        0xf7ff1d28, 0x4669fee1, 0xf7ff4851, 0xbd38ff84, 0x4604b538, 0x447d4d4b, 0x494d3df6, 0xf7ff4628,
        0x4621fed3, 0xf7ff1d28, 0x4669fecf, 0xf7ff4848, 0xbd38ff72, 0x4c47b518, 0x4947447c, 0xf7ff4620,
        0x4669fec3, 0xf7ff4844, 0xbd18ff66, 0x4606b570, 0x2500460c, 0x4630e00a, 0xffb6f7ff, 0x2d004605,
        0xe005d000, 0x36ff36ff, 0x1e643602, 0xd1f22c00, 0x4628bf00, 0xb510bd70, 0x21402400, 0x06802005,
        0xffe4f7ff, 0x46204604, 0xb5f8bd10, 0x460e4605, 0x4c304617, 0x3c5c447c, 0x46204930, 0xfe94f7ff,
        0x310721ff, 0xf7ff1d20, 0x4629fe8f, 0x30084620, 0xfe8af7ff, 0x46204631, 0xf7ff300c, 0x4669fe85,
        0xf7ff4826, 0xbdf8ff28, 0x4605b5f8, 0x4617460e, 0x447c4c20, 0x49223c9a, 0xf7ff4620, 0x21fffe75,
        0x1d203107, 0xfe70f7ff, 0x46204629, 0xf7ff3008, 0x4631fe6b, 0x300c4620, 0xfe66f7ff, 0x48184669,
        0xff09f7ff, 0xb570bdf8, 0xb081b0ff, 0x26004605, 0xe0032400, 0x46692000, 0x1c645508, 0x02402001,
        0xdbf74284, 0x46694602, 0xf7ff4628, 0x4606ffcd, 0xb07f4630, 0xbd70b001, 0x00000d05, 0x40200000,
        0x40220000, 0x00000240, 0x40221008, 0x1c000100, 0x14000100, 0x00000128, 0x0a000100, 0x06000100,
        0x05000100, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000
    ],

    # Relative function addresses
    'pc_init': 0x08000021,
    'pc_unInit': 0x08000027,
    'pc_program_page': 0x08000041,
    'pc_erase_sector': 0x08000035,
    'pc_eraseAll': 0x0800002d,

    'static_base': 0x08000000 + 0x00000020 + 0x000009f8,
    'begin_stack': 0x08000d00,
    'begin_data': 0x08000000 + 0x1000,
    'page_size': 0x200,
    'analyzer_supported': False,
    'analyzer_address': 0x00000000,
    'page_buffers': [0x08001000, 0x08001200],  # Enable double buffering
    'min_program_length': 0x200,

    # Flash information
    'flash_start': 0x14000000,
    'flash_size': 0x8000,
    'sector_sizes': (
        (0x0, 0x200),
    )
}

flash_algo_sflash = {
    'load_address': 0x08000000,

    # Flash algorithm as a hex string
    'instructions': [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x20004603, 0x46014770, 0x47702000, 0xf000b510, 0xbd10f9aa, 0x4604b510, 0xf0004620, 0xbd10f976,
        0x4606b570, 0x4615460c, 0x46294622, 0xf0004630, 0xbd70f94d, 0x4604b570, 0x4616460d, 0x46294632,
        0xf0004620, 0xbd70f81f, 0x47706001, 0x600a6802, 0x21004770, 0x1c49e000, 0x43424ae4, 0xd8fa428a,
        0xb5084770, 0x48e24669, 0xfff0f7ff, 0x0209210f, 0x40089800, 0xd1012800, 0xe0002001, 0x46032000,
        0xbd084618, 0x4603b570, 0x461d460c, 0xe0052100, 0x5c6e5c50, 0xd00042b0, 0x1c49e002, 0xd3f742a1,
        0x1858bf00, 0xb5febd70, 0x460b4605, 0x20004616, 0x24009002, 0x01682700, 0x184049ce, 0xbf009000,
        0x9800a901, 0xf7ff301c, 0x9801ffc1, 0x2b000fc7, 0x2f00d001, 0x2b00d103, 0x2f00d103, 0x2001d101,
        0x2000e000, 0x2c004604, 0x9802d109, 0xd90042b0, 0x2001e007, 0xffadf7ff, 0x1c409802, 0x2c009002,
        0xbf00d0de, 0x21014620, 0xbdfe4048, 0x4604b5f8, 0x2600460d, 0x01602300, 0x184749b6, 0x4669bf00,
        0xf7ff4638, 0x9800ff93, 0x2b000fc3, 0x42aed106, 0xe005d900, 0xf7ff2001, 0x1c76ff8c, 0xd0ee2b00,
        0x4618bf00, 0x40482101, 0xb5f0bdf8, 0x460d4607, 0x26004613, 0xbf002400, 0x46384619, 0xff76f7ff,
        0x0f006818, 0x21050700, 0x42880749, 0x2001d101, 0x2000e000, 0x2c004604, 0x42aed106, 0xe005d900,
        0xf7ff2001, 0x1c76ff66, 0xd0e52c00, 0x4620bf00, 0x40482101, 0xb5f3bdf0, 0x4606b082, 0x48962700,
        0x90014478, 0x0fc007f0, 0x40482101, 0x25009000, 0xff57f7ff, 0xd0022800, 0x4d8e2400, 0x2401e002,
        0x35204d8c, 0x31f521ff, 0xf7ff4620, 0x4607ff9f, 0xd1362f00, 0x28009800, 0x4628d005, 0x9901300c,
        0xff32f7ff, 0x4631e004, 0x300c4628, 0xff2cf7ff, 0x30104620, 0x40822201, 0x48804611, 0xff24f7ff,
        0x46282101, 0xf7ff3008, 0x22ffff1f, 0x210032f5, 0xf7ff4620, 0x4607ff48, 0xd1122f00, 0x28009800,
        0x21ffd007, 0x9a0331f5, 0xf7ff9801, 0x4607ff8e, 0x21ffe007, 0x462831f5, 0x9a03300c, 0xff85f7ff,
        0x46384607, 0xbdf0b004, 0x4604b538, 0x447d4d6a, 0x496b3dae, 0xf7ff4628, 0x4621fef7, 0xf7ff1d28,
        0x4669fef3, 0xf7ff4866, 0xbd38ff96, 0x4604b538, 0x447d4d61, 0x49633dd2, 0xf7ff4628, 0x4621fee5,
        0xf7ff1d28, 0x4669fee1, 0xf7ff485e, 0xbd38ff84, 0x4604b538, 0x447d4d58, 0x495a3df6, 0xf7ff4628,
        0x4621fed3, 0xf7ff1d28, 0x4669fecf, 0xf7ff4855, 0xbd38ff72, 0x4c54b518, 0x4954447c, 0xf7ff4620,
        0x4669fec3, 0xf7ff4851, 0xbd18ff66, 0x4605b5f8, 0x4617460e, 0x447c4c4c, 0x494d3c1e, 0xf7ff4620,
        0x21fffeb3, 0x1d203107, 0xfeaef7ff, 0x46204629, 0xf7ff3008, 0x4631fea9, 0x300c4620, 0xfea4f7ff,
        0x48434669, 0xff47f7ff, 0xb570bdf8, 0xb081b0ff, 0x26004605, 0xe0032400, 0x46692000, 0x1c645508,
        0x02402001, 0xdbf74284, 0x46694602, 0xf7ff4628, 0x4606ffcd, 0xb07f4630, 0xbd70b001, 0x4606b570,
        0x2500460c, 0x4630e00a, 0xffdff7ff, 0x2d004605, 0xe005d000, 0x36ff36ff, 0x1e643602, 0xd1f22c00,
        0x4628bf00, 0xb510bd70, 0xbf002400, 0x48292104, 0xffe4f7ff, 0x2c004604, 0xe015d000, 0x48262101,
        0xffdcf7ff, 0x2c004604, 0xe00dd000, 0x48232106, 0xffd4f7ff, 0x2c004604, 0xe005d000, 0x48202102,
        0xffccf7ff, 0xbf004604, 0x4620bf00, 0xb5f8bd10, 0x460e4605, 0x4c1b4617, 0x491b447c, 0xf7ff4620,
        0x21fffe43, 0x1d203107, 0xfe3ef7ff, 0x46204629, 0xf7ff3008, 0x4631fe39, 0x300c4620, 0xfe34f7ff,
        0x48114669, 0xfed7f7ff, 0x0000bdf8, 0x00000d05, 0x40200000, 0x40220000, 0x00000288, 0x40221008,
        0x1c000100, 0x14000100, 0x00000170, 0x0a000100, 0x05000100, 0x16000800, 0x16001a00, 0x16005a00,
        0x16007c00, 0x00000070, 0x06000100, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
        0x00000000
    ],

    # Relative function addresses
    'pc_init': 0x08000021,
    'pc_unInit': 0x08000027,
    'pc_program_page': 0x08000041,
    'pc_erase_sector': 0x08000035,
    'pc_eraseAll': 0x0800002d,

    'static_base': 0x08000000 + 0x00000020 + 0x00000a40,
    'begin_stack': 0x08000d00,
    'begin_data': 0x08000000 + 0x1000,
    'page_size': 0x200,
    'analyzer_supported': False,
    'analyzer_address': 0x00000000,
    'page_buffers': [0x08001000, 0x08001200],  # Enable double buffering
    'min_program_length': 0x200,

    # Flash information
    'flash_start': 0x16000000,
    'flash_size': 0x8000,
    'sector_sizes': (
        (0x0, 0x200),
    )
}


class PSoC6FlashCommon(Flash):
    def __init__(self, target, flash_algo):
        super(PSoC6FlashCommon, self).__init__(target, flash_algo)

    def get_flash_info(self):
        info = super(PSoC6FlashCommon, self).get_flash_info()
        # Time it takes to perform a chip erase
        info.erase_weight = 0.5

        return info

    def get_page_info(self, addr):
        info = super(PSoC6FlashCommon, self).get_page_info(addr)
        if info is not None:
            # Time it takes to erase a page
            info.erase_weight = 0.05
            # Time it takes to program a page (Not including data transfer time)
            info.program_weight = 0.07

        return info


class Flash_CY8C6xxA_Main(PSoC6FlashCommon):
    def __init__(self, target):
        super(Flash_CY8C6xxA_Main, self).__init__(target, flash_algo_main)


class Flash_CY8C6xxA_Work(PSoC6FlashCommon):
    def __init__(self, target):
        super(Flash_CY8C6xxA_Work, self).__init__(target, flash_algo_work)


class Flash_CY8C6xxA_SFlash(PSoC6FlashCommon):
    def __init__(self, target):
        super(Flash_CY8C6xxA_SFlash, self).__init__(target, flash_algo_sflash)


class CY8C6xxA(CoreSightTarget):
    memoryMap = MemoryMap(
        RomRegion(start=0x00000000, length=0x20000),
        FlashRegion(start=0x10000000, length=0x200000, blocksize=0x200, is_boot_memory=True, erased_byte_value=0,
                    algo=flash_algo_main, flash_class=Flash_CY8C6xxA_Main),
        FlashRegion(start=0x14000000, length=0x8000, blocksize=0x200, is_boot_memory=False, erased_byte_value=0,
                    algo=flash_algo_work, flash_class=Flash_CY8C6xxA_Work),
        FlashRegion(start=0x16000000, length=0x8000, blocksize=0x200, is_boot_memory=False, erased_byte_value=0,
                    is_testable=False, algo=flash_algo_sflash, flash_class=Flash_CY8C6xxA_SFlash),
        RamRegion(start=0x08000000, length=0x10000)
    )

    def __init__(self, link):
        super(CY8C6xxA, self).__init__(link, self.memoryMap)

    def create_init_sequence(self):
        seq = super(CY8C6xxA, self).create_init_sequence()
        seq.replace_task('create_cores', self.create_cy8c6xx7_core)
        return seq

    def create_cy8c6xx7_core(self):
        core0 = CortexM_CY8C6xxA(self, self.aps[1], self.memory_map, 0)
        core0.default_reset_type = self.ResetType.SW_SYSRESETREQ
        core1 = CortexM_CY8C6xxA(self, self.aps[2], self.memory_map, 1)
        core1.default_reset_type = self.ResetType.SW_SYSRESETREQ

        self.aps[1].core = core0
        self.aps[2].core = core1
        core0.init()
        core1.init()
        self.add_core(core0)
        self.add_core(core1)


class CortexM_CY8C6xxA(CortexM):
    # VectorTableBase registers for the cores
    VTBASE_CM0 = 0x40201120
    VTBASE_CM4 = 0x40200200

    # Main Flash addresses
    MFLASH_START = 0x10000000
    MFLASH_END = 0x10200000
    
    def reset(self, reset_type=None):
        self.notify(Notification(event=Target.EVENT_PRE_RESET, source=self))

        self._run_token += 1

        if reset_type is Target.ResetType.HW:
            self.session.probe.reset()
            sleep(0.5)
            self._ap.dp.init()
            self._ap.dp.power_up_debug()
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

        start_time = time()
        while time() - start_time < 5.0:
            try:
                dhcsr_reg = self.read32(CortexM.DHCSR)
                if (dhcsr_reg & CortexM.S_RESET_ST) == 0:
                    break
            except exceptions.TransferError:
                self.flush()
                self._ap.dp.init()
                self._ap.dp.power_up_debug()
                sleep(0.01)

        self.notify(Notification(event=Target.EVENT_POST_RESET, source=self))

    def wait_halted(self):
        start_time = time()
        while time() - start_time < 5.0:
            try:
                if not self.is_running():
                    return
            except exceptions.TransferError:
                self.flush()
                sleep(0.01)

        raise Exception("Timeout waiting for target halt")

    def reset_and_halt(self, reset_type=None):
        self.halt()
        self.reset(reset_type)
        sleep(0.5)
        self.halt()

        self.wait_halted()

        if self.core_number == 0:
            vtbase = self.read_memory(self.VTBASE_CM0)
        elif self.core_number == 1:
            vtbase = self.read_memory(self.VTBASE_CM4)
        else:
            raise Exception("Invalid CORE ID")

        vtbase &= 0xFFFFFF00
        if vtbase < self.MFLASH_START or vtbase > self.MFLASH_END:
            logging.info("Vector Table address invalid (0x%08X), will not halt at main()", vtbase)
            return

        entry = self.read_memory(vtbase + 4)
        if entry < self.MFLASH_START or entry > self.MFLASH_END:
            logging.info("Entry Point address invalid (0x%08X), will not halt at main()", entry)
            return

        self.set_breakpoint(entry)
        self.reset(self.ResetType.SW_SYSRESETREQ)
        sleep(0.2)
        self.wait_halted()
        self.remove_breakpoint(entry)
