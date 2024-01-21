#!/usr/bin/env python3
import sys
from fitparse import FitFile
fitData = FitFile(sys.argv[1])
x = next(fitData.get_messages('zones_target'))
zone = x.get_value('max_heart_rate')
x = next(fitData.get_messages('session'))
sess = x.get_value('max_heart_rate')
print(f'zone max: {zone} this session: {sess}')
