#!/usr/bin/env python3
#
# Copyright (c) 2023 Adam Baker
# Decode photos of Life Fitness QR codes to extract the
# exercise statistics

import argparse
import base64
import datetime
import exif
import json
import os
from PIL import Image, ImageFilter
from pyzbar.pyzbar import decode

verbose = 2
# Maximum time difference for two images to be considered the same code
timedelta = 90


def find_images(srcpath):
    images = []
    files = [f for f in os.listdir(srcpath)]
    for name in files:
        name = os.path.join(srcpath, name)
        try:
            f = open(name, 'rb')
        except OSError:
            continue
        try:
            timestr = exif.Image(f).datetime
        except KeyError:
            f.close()
            continue
        filetime = datetime.datetime.strptime(timestr, '%Y:%m:%d %H:%M:%S')
        images.append((name, filetime))
    return images


def batch_images(images, timedelta, verbose):
    batches = []
    for image in images:
        added = False
        for batch in batches:
            timediff = batch[0][1] - image[1]
            if (timediff.total_seconds() < timedelta) and (timediff.total_seconds() > -timedelta):
                added = True
                batch.append(image)
                if verbose > 1:
                    print(f'Added image {image[0]} to batch {batch[0][0]}, timediff = {timediff.total_seconds()}')
                break
        if not added:
            batches.append([image])
    return batches


def decode_images(batches, verbose):
    raw = 0
    usm = 0
    smooth = 0

    result = []

    for batch in batches:
        done = False
        for image in batch:
            img = Image.open(image[0])
            decoded = decode(img)
            if len(decoded) != 0:
                done = True
                raw += 1
                if verbose > 0:
                    print(f'Decoded image {image[0]} in raw mode')
                break
            else:
                img2 = img.filter(ImageFilter.UnsharpMask(radius=4, percent=400, threshold=0))
                img2 = img2.filter(ImageFilter.GaussianBlur(radius=3))
                decoded = decode(img2)
            if len(decoded) != 0:
                done = True
                usm += 1
                if verbose > 0:
                    print(f'Decoded image {image[0]} in usm mode')
                break
            else:
                img2 = img.filter(ImageFilter.GaussianBlur(radius=3))
                decoded = decode(img2)
            if len(decoded) != 0:
                done = True
                smooth += 1
                if verbose > 0:
                    print(f'Decoded image {image[0]} in smooth mode')
                break
        if done:
            url = decoded[0].data
            js = base64.b64decode(url[url.find(b'&r=') + 3:])
            result.append(json.loads(js))
        else:
            print(f'Decode failed for batch {batch[0][0]}')
    if verbose > 0:
        print(f'Decode counts: raw {raw}, usm {usm}, smooth {smooth}')
    return result


activity = {
        '137': 'Treadmill',
        '138': 'X-Train',
        '139': 'Cycling'
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("srcpath",
                        help="Directory comtaining the images to scan")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbose mode, more -v flags increase verbosity")
    parser.add_argument("-j", "--json",
                        help="JSON format output file, appended to if already exists")
    args = parser.parse_args()

    images = find_images(args.srcpath)
    batches = batch_images(images, 90, args.verbose)
    sessions = decode_images(batches, args.verbose)
    sessions = sorted(sessions, key=lambda d: d["dt"])
    if args.json:
        try:
            with open(args.json, "r") as f:
                old_sessions = json.load(f)
        except IOError:
            old_sessions = []
        [sessions.append(item) for item in old_sessions if item not in sessions]
        sessions = sorted(sessions, key=lambda d: d["dt"])
        with open(args.json, "w") as f:
            json.dump(sessions, f)
    for session in sessions:
        ts = datetime.datetime.fromisoformat(session["dt"])
        h1 = int(session["et"]) // 3600
        m1 = int(session["et"]) // 60 - h1 * 60
        s1 = int(session["et"]) - h1 * 3600 - m1 * 60
        h2 = int(float(session["dc"]["v"]) // 3600)
        m2 = int(float(session["dc"]["v"]) // 60 - h2 * 60)
        s2 = float(session["dc"]["v"]) - h2 * 3600 - m2 * 60
        print(ts.strftime('%Y/%m/%d, %H:%M:%S,') +
              f' {h1:02d}:{m1:02d}:{s1:02d}, {h2:02d}:{m2:02d}:{s2:5.2f}, , {activity[session["t"]]},' +
              f' {session["d"]["v"]}, , {session["as"]["v"]}, , {session["c"]}, , {session["ahr"]}')
