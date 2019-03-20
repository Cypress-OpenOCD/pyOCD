"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2018 ARM Limited

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

flash_algo = {
    'load_address' : 0x08000000,

    # Flash algorithm as a hex string
    'instructions': [
    0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
    0xb0822300, 0x4b059301, 0x9a014343, 0xd8014293, 0x4770b002, 0x32019a01, 0xe7f69201, 0x00000d05,
    0x68184b04, 0x011b23f0, 0x42434018, 0xb2c04158, 0x46c04770, 0x40210400, 0x000eb5f8, 0x25000017,
    0x18c04b09, 0x69200144, 0xd0082e00, 0xd1080fc0, 0xd80642bd, 0xf7ff3001, 0x3501ffd3, 0x43c0e7f3,
    0x2301e7f4, 0xbdf84058, 0x02011800, 0x000db570, 0x4b082600, 0x014418c0, 0x28006820, 0x42aedb06,
    0x2001d804, 0xffbcf7ff, 0xe7f53601, 0x0fc043c0, 0x46c0bd70, 0x02011800, 0x27a0b5f0, 0x00160005,
    0xb0832400, 0x063f9101, 0x60306828, 0x07000f00, 0xd00742b8, 0x429c9b01, 0x2001d804, 0xffa0f7ff,
    0xe7f13401, 0x05db23c0, 0x1e4318c0, 0xbdfe4198, 0xb085b5f0, 0x000e0007, 0xffa2f7ff, 0xd10b2800,
    0x4c1d2501, 0x002821fa, 0xf7ff0049, 0x2800ffbf, 0x6830d005, 0xbdf0b005, 0x25004c18, 0x4b18e7f2,
    0x447b003a, 0x23019302, 0x9201401a, 0x320c0022, 0x9a019203, 0xd11d2a00, 0x60e29a02, 0x0019002a,
    0x40913210, 0x00284a0f, 0x22fa6011, 0x005260a3, 0xf7ff2100, 0x2800ff81, 0x21fad1db, 0x00329b01,
    0x98020049, 0xd0002b00, 0xf7ff9803, 0x2800ffa5, 0xe7ced0d0, 0xe7e160e7, 0x40230020, 0x40230000,
    0x00000136, 0x40231008, 0x2300b570, 0x19180004, 0xd100428b, 0x7805bd70, 0x42ae5cd6, 0x3301d1fa,
    0x1809e7f5, 0xd1014288, 0x47702000, 0x30017803, 0xd0f74293, 0xe7f82001, 0x4b05b500, 0xb0834a05,
    0x601a447b, 0x6058a901, 0xf7ff0010, 0xbd0eff91, 0x00000098, 0x1c000100, 0x4b05b500, 0xb0834a05,
    0x601a447b, 0x6058a901, 0xf7ff0010, 0xbd0eff81, 0x00000078, 0x14000100, 0x2483b510, 0x4a074b06,
    0xb082447b, 0x601a0064, 0x6098605c, 0x001060d9, 0xf7ffa901, 0xbd16ff6d, 0x00000058, 0x06000100,
    0x47702000, 0x47702000, 0xb51020a0, 0xf7ff0540, 0xbd10ffd3, 0xf7ffb510, 0xbd10ffbf, 0xb5100013,
    0x0019000a, 0xffd8f7ff, 0xb510bd10, 0xff9cf7ff, 0xb510bd10, 0xffa5f7ff, 0x0000bd10, 0x00000000,
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
    0x00000000, 0x00000000, 0x00000000, 0x00000000
    ],

    # Relative function addresses
    'pc_init': 0x08000221,
    'pc_unInit': 0x08000225,
    'pc_program_page': 0x0800023d,
    'pc_erase_sector': 0x08000235,
    'pc_eraseAll': 0x08000229,

    'static_base' : 0x08000000 + 0x00000020 + 0x0000023c,
    'begin_stack' : 0x08000b00,
    'begin_data' : 0x08000000 + 0x1000,
    'page_size' : 0x200,
    'analyzer_supported' : False,
    'analyzer_address' : 0x00000000,
    'page_buffers' : [0x08001000, 0x08001200],   # Enable double buffering
    'min_program_length' : 0x200,

    # Flash information
    'flash_start': 0x14000000,
    'flash_size': 0x8000,
    'sector_sizes': (
        (0x0, 0x200),
    )
}
