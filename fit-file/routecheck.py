#!/usr/bin/env python3

import argparse
import csv
import fitparse
import math
import os.path

LAT_TO_METRES = 111320
FIT_TO_DEGREES = (2**32) / 360
METRES_TO_MILES = 0.000621371
SECONDS_PER_HOUR = 3600

CODE = 2
LAT = 1
LON = 0
NAME = 3


def routeCheck(fitFile, waypointFile, tolerance, summary, fullName, lapTimes):
    # read the waypoints data
    waypoints = []
    try:
        with open(waypointFile, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                waypoints.append(row)
    except OSError:
        print("Error opening waypoint file")
        return

    # initialise the fit file reader
    lastWaypoint = -1
    try:
        fitData = fitparse.FitFile(fitFile)
    except fitparse.FitParseError as e:
        print(f"Error reading {fitFile}: {e}")
        return

    # calculate location match tolerances
    # Assumes the first waypoint will be close enough to the others that calculating
    # a conversion from metres to degrees longitude there wil be valid for the other
    # points
    toleranceLat = abs(tolerance / LAT_TO_METRES)
    toleranceLon = toleranceLat / math.cos(math.radians(float(waypoints[0][LAT])))

    # Gather the list of start / stop times so we don't count moving time
    # while the GPS is stopped
    events = fitData.get_messages('event')
    starts = []
    for event in events:
        if event.get('event_type').value == 'start':
            starts.append(event.get('timestamp').value)

    # For each FIT record check if it is near to a new waypoint
    routeString = ""
    start = 0
    records = fitData.get_messages('record')
    moving = 0
    lastTime = None
    for record in records:
        found = False
        try:
            lat = record.get('position_lat').value / FIT_TO_DEGREES
            lon = record.get('position_long').value / FIT_TO_DEGREES
            speed = record.get('enhanced_speed').value
        except AttributeError:
            continue
        now = record.get('timestamp').value
        if lastTime is not None:
            if len(starts) > start + 1 and starts[start + 1] <= now:
                start += 1
            else:
                if speed > 0:
                    moving += (now - lastTime).seconds
        lastTime = now
        for index, waypoint in enumerate(waypoints):
            sqrDist = (((float(waypoint[LAT]) - lat) / toleranceLat) ** 2 +
                       ((float(waypoint[LON]) - lon) / toleranceLon) ** 2)
            if sqrDist < 1:
                found = True
                currentWaypoint = index
                break
        if found and currentWaypoint != lastWaypoint:
            if fullName:
                routeString += waypoints[currentWaypoint][NAME] + "\n"
            else:
                routeString += waypoints[currentWaypoint][CODE]
            lastWaypoint = currentWaypoint

    # Output summary if enabled
    if summary:
        session = next(fitData.get_messages('session'))
        speed = (session.get_value('enhanced_avg_speed') *
                 METRES_TO_MILES * SECONDS_PER_HOUR)
        try:
            maxSpeed = (session.get_value('enhanced_max_speed') *
                        METRES_TO_MILES * SECONDS_PER_HOUR)
        except TypeError:
            maxSpeed = 0
        time = int(session.get_value('total_timer_time'))
        hours = time // 3600
        mins = time // 60 - hours * 60
        secs = time - hours * 3600 - mins * 60
        movHours = moving // 3600
        movMins = moving // 60 - movHours * 60
        movSecs = moving - movHours * 3600 - movMins * 60
        print(session.get_value('start_time').strftime('%Y/%m/%d, %H:%M:%S, ') +
              f'{hours:02d}:{mins:02d}:{secs:02d}, ' +
              f'{movHours:02d}:{movMins:02d}:{movSecs:02d}, ' +
              os.path.basename(fitFile) +
              ', ' + str(session.get_value('sub_sport')) +
              f", {session.get_value('total_distance') * METRES_TO_MILES:.6f}" +
              ', ' + str(session.get_value('total_ascent')) +
              f", {speed:.6f}" +
              f", {maxSpeed:.6f}" +
              ', ' + str(session.get_value('total_calories')) +
              ', ' + str(session.get_value('avg_temperature')) +
              ', ' + str(session.get_value('avg_heart_rate')) +
              ', ' + str(session.get_value('max_heart_rate')), end='')
        if fullName:
            print()
        else:
            print(', ', end='')

    print(routeString, end='')

    # Output lap times if enabled
    if lapTimes:
        if not fullName:
            print(',', end='')
        laps = fitData.get_messages('lap')
        for lap in laps:
            elapsed = lap.get_value('total_elapsed_time')
            distance = lap.get_value('total_distance') * METRES_TO_MILES
            if fullName:
                print(f' {int(elapsed // 60)}:{int(elapsed % 60):02d}, {distance:.5f}')
            else:
                print(f' {int(elapsed // 60)}:{int(elapsed % 60):02d}', end='')

    if not fullName:
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("fitfile",
                        help="Garmin FIT format position log file")
    parser.add_argument("waypoints",
                        help="CSV format list of waypoints to check for")
    parser.add_argument('--full', '-f', action='store_true',
                        help='Show full place names rather than codes')
    parser.add_argument('--lap_times', '-l', action='store_true',
                        help='Include lap time stats')
    parser.add_argument('--summary', '-s', action='store_true',
                        help='Include FIT file session summary')
    parser.add_argument('--tolerance', '-t', type=int, default=25,
                        help='Position tolerance in metres')
    args = parser.parse_args()
    routeCheck(args.fitfile, args.waypoints, args.tolerance, args.summary,
               args.full, args.lap_times)
