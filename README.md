A set of utilities to process data from fitness activities

# fit-file

Utilities to work with the Garmin .FIT file format

## fit_totals.py

Produce a summary of journet statistics for every .FIT file in the
provided directory.

## hr_graph.py

Produce a graph of heartrate and speed against time

## max_hr.py

Display the maximum heart rate values recorded in a .FIT file

## message-types.py

Print one of each type of message in the supplied file - useful for
debugging.

## routecheck.py

Compare the locations in a .FIT file to the supplied waypoint file (in
Garmin CSV POI file format) to display a text string indicating the route
taken and an optional summary of journey statistics.

# life-fitness

## decode.py

Decode a directory of photos of QR codes obtained from Life Fitness
exercise macines to extract the JSON activity record and then convert
it to CSV. Assumes that if several photos are taken around the same time
they are all from the same activity and only one needs decoding. Can be
provided with an empty image directory to convert an existing JSON file
to CSV

# common

## stats.py

Produce an month by month summary of activity based upon a CSV file from
routecheck.py or decode.py

Column headings for those CSV files are

Date, Start, Total Time, Moving Time, File, Activity, Distance, Ascent, Avg. Speed, Max.Speed, Calories, Temp, Avg. HR, Max. HR, Route, Lap Times

#TODO
* Check units are consistent between FIT file and LF


Test data is from https://github.com/andrewcooke/choochoo/blob/master/data/test/source/personal/
