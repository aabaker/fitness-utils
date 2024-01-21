#!/usr/bin/env python3
#
# Copyright © Adam Baker 2024
#
# SPDX-License-Identifier: MIT
#
# A program to extract the first message of each data type from a Garmin FIT format file
#

import fitparse
import sys

seen = []

try:
    fitData = fitparse.FitFile(sys.argv[1])
except fitparse.FitParseError as e:
    print(f"Error reading .FIT file: {e}")
    sys.exit(1)

for msg in fitData.messages:
    if msg.name not in seen:
        print(msg.as_dict())
        print()
        seen.append(msg.name)
