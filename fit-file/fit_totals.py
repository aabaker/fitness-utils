#!/usr/bin/env python3

from fitparse import FitFile
import sys

METRES_TO_MILES = 0.000621
SECONDS_PER_HOUR = 3600

print('Date, Start Time, Duration, Category, Distance, Ascent, Average Speed, Calories, ' +
      'Average Temperature, Average HR, Max HR')

total_distance = 0
total_time = 0
total_calories = 0
total_ascent = 0

for file in sys.argv[1:]:
    fitfile = FitFile(file)

    session = next(fitfile.get_messages('session'))

    total_distance += session.get_value('total_distance')
    time = session.get_value('total_elapsed_time')
    total_time += time
    hours = int(time / 3600)
    mins = int(time / 60 - hours * 60)
    secs = int(time - hours * 3600 - mins * 60)
    total_calories += session.get_value('total_calories')
    ascent = session.get_value('total_ascent')
    if ascent is not None:
        total_ascent += ascent
    speed = (session.get_value('enhanced_avg_speed') *
             METRES_TO_MILES * SECONDS_PER_HOUR)

    print(session.get_value('start_time').strftime('%-d/%b/%Y, %H:%M:%S') +
          ', ' + '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs) +
          ', ' + str(session.get_value('sub_sport')) +
          f", {session.get_value('total_distance') * METRES_TO_MILES:.6f}" +
          ', ' + str(session.get_value('total_ascent')) +
          f", {speed:.6f}" +
          ', ' + str(session.get_value('total_calories')) +
          ', ' + str(session.get_value('avg_temperature')) +
          ', ' + str(session.get_value('avg_heart_rate')) +
          ', ' + str(session.get_value('max_heart_rate')))

print('Totals, , ' + str(total_time) +
      ', , ' + str(total_distance * METRES_TO_MILES) +
      ', ' + str(total_ascent) +
      ', , ' + str(total_calories))
