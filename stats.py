#!/usr/bin/env python3

import csv
import sys
import calendar
import time

# CSV column numbers
DATE = 0
START_TIME = 1
TOTAL_TIME = 2
MOVING_TIME = 3
SRC_FILE = 4
CATEGORY = 5
DISTANCE = 6
ASCENT = 7
AVG_SPEED = 8
MAX_SPEED = 9
CALORIES = 10
TEMP = 11
AVG_HR = 12
MAX_HR = 13
ROUTE = 14


def formatDuration(seconds):
    hours = seconds // 3600
    minutes = (seconds - hours * 3600) // 60
    seconds = (seconds - hours * 3600 - minutes * 60)
    return f"{hours}:{minutes:0{2}}:{seconds:0{2}}"


class Month:
    def __init__(self, num):
        self.num = num
        self.miles = 0
        self.moving = 0
        self.rides = 0
        self.temp = 0
        self.avgSpeed = 0
        self.maxSpeed = None

    def update(self, movingTime, miles, ascent, avgSpeed, maxSpeed, temp):
        self.miles += float(miles)
        self.moving += movingTime
        self.rides += 1
        self.temp += float(temp)
        self.avgSpeed += float(avgSpeed)
        maxSpeed = float(maxSpeed)
        if not self.maxSpeed or self.maxSpeed < maxSpeed:
            self.maxSpeed = maxSpeed

    def print(self):
        print(f"{calendar.month_abbr[self.num]}: {self.miles:.2f} Miles, {formatDuration(self.moving)} Hours, "
              f"{self.rides} Rides, {self.avgSpeed / self.rides:.2f} Average Speed, "
              f"{self.maxSpeed:.2f} Max Speed, {self.temp / self.rides:.1f} Average Temp")


totalTime = 0
totalMiles = 0
routes = {}

months = [Month(i) for i in range(1, 13)]
with open(sys.argv[1], "r") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        date = time.strptime(row[DATE], "%Y/%m/%d")
        h, m, s = row[MOVING_TIME].split(":")
        moving = int(h) * 3600 + int(m) * 60 + int(s)
        months[date.tm_mon - 1].update(moving, row[DISTANCE], row[ASCENT],
                                       row[AVG_SPEED], row[MAX_SPEED], row[TEMP])
        totalTime += moving
        totalMiles += float(row[DISTANCE])
        # Check if route starts and ends at same point
        route = row[ROUTE].strip()
        if len(route) > 0 and route[0] == route[-1:]:
            try:
                routes[route] += 1
            except KeyError:
                routes[route] = 1

for month in months:
    month.print()

routeList = []
for route in routes.items():
    routeList.append(route)
routeList.sort(key=lambda a: a[1], reverse=True)
for i in routeList[0:min(10, len(routeList))]:
    print(f"{i[0]} : {i[1]}")

print(f"Total mileage {totalMiles:.2f}, total time {formatDuration(totalTime)}")
