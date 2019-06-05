# pyOCD debugger
# Copyright (c) 2015 Arm Limited
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
from ..core.target import Target
from ..core.options import OPTIONS_INFO
from ..utility.compatibility import to_str_safe

LOG = logging.getLogger(__name__)

def split_command_line(cmd_line):
    """! @brief Split command line by whitespace, supporting quoted strings."""
    result = []
    if type(cmd_line) is str:
        args = [cmd_line]
    else:
        args = cmd_line
    for cmd in args:
        state = 0
        word = ''
        open_quote = ''
        for c in cmd:
            if state == 0:
                if c in (' ', '\t', '\r', '\n'):
                    if word:
                        result.append(word)
                        word = ''
                elif c in ('"', "'"):
                    open_quote = c
                    state = 1
                else:
                    word += c
            elif state == 1:
                if c == open_quote:
                    result.append(word)
                    word = ''
                    state = 0
                else:
                    word += c
        if word:
            result.append(word)
    return result

## Map of vector char characters to masks.
VECTOR_CATCH_CHAR_MAP = {
        'h': Target.CATCH_HARD_FAULT,
        'b': Target.CATCH_BUS_FAULT,
        'm': Target.CATCH_MEM_FAULT,
        'i': Target.CATCH_INTERRUPT_ERR,
        's': Target.CATCH_STATE_ERR,
        'c': Target.CATCH_CHECK_ERR,
        'p': Target.CATCH_COPROCESSOR_ERR,
        'r': Target.CATCH_CORE_RESET,
        'a': Target.CATCH_ALL,
        'n': Target.CATCH_NONE,
    }

def convert_vector_catch(value):
    """! @brief Convert a vector catch string to a mask.
    
    @exception ValueError Raised if an invalid vector catch character is encountered.
    """
    # Make case insensitive.
    value = to_str_safe(value).lower()

    # Handle special vector catch options.
    if value == 'all':
        return Target.CATCH_ALL
    elif value == 'none':
        return Target.CATCH_NONE

    # Convert options string to mask.
    try:
        return sum([VECTOR_CATCH_CHAR_MAP[c] for c in value])
    except KeyError as e:
        # Reraise an error with a more helpful message.
        raise ValueError("invalid vector catch option '{}'".format(e.args[0]))

def convert_session_options(option_list):
    """! @brief Convert a list of session option settings to a dictionary."""
    options = {}
    if option_list is not None:
        for o in option_list:
            if '=' in o:
                name, value = o.split('=', 1)
                name = name.strip().lower()
                value = value.strip()
            else:
                name = o.strip().lower()
                value = None
            
            # Look for this option.
            try:
                info = OPTIONS_INFO[name]
            except KeyError:
                LOG.warning("ignoring unknown session option '%s'", name)
                continue

            # Handle bool options without a value specially.
            if value is None:
                if info.type is bool:
                    if name.startswith('no-'):
                        name = name[3:]
                        value = False
                    else:
                        value = True
                else:
                    LOG.warning("non-boolean option '%s' requires a value", name)
                    continue
            # Convert string value to option type.
            elif info.type is bool:
                value = value in ("true", "1", "yes", "on")
            elif info.type is int:
                try:
                    value = int(value, base=0)
                except ValueError:
                    LOG.warning("invalid value for option '%s'", name)
            
            options[name] = value
    return options

## Map to convert from reset type names to enums.
RESET_TYPE_MAP = {
        'default': None,
        'hw': Target.ResetType.HW,
        'sw': Target.ResetType.SW,
        'hardware': Target.ResetType.HW,
        'software': Target.ResetType.SW,
        'sw_sysresetreq': Target.ResetType.SW_SYSRESETREQ,
        'sw_vectreset': Target.ResetType.SW_VECTRESET,
        'sw_emulated': Target.ResetType.SW_EMULATED,
        'sysresetreq': Target.ResetType.SW_SYSRESETREQ,
        'vectreset': Target.ResetType.SW_VECTRESET,
        'emulated': Target.ResetType.SW_EMULATED,
    }

def convert_reset_type(value):
    """! @brief Convert a reset_type session option value to the Target.ResetType enum.
    @param value The value of the reset_type session option.
    @exception ValueError Raised if an unknown reset_type value is passed.
    """
    value = value.lower()
    if value not in RESET_TYPE_MAP:
        raise ValueError("unexpected value for reset_type option ('%s')" % value)
    return RESET_TYPE_MAP[value]

