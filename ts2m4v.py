# -*- coding: utf8 -*-
"""
Usage
----------------------------------

Specify Directory that has TS files.
::

  python ts2mv4.py INPUT_DIR OUTPUT_DIR

If OUTPUT_DIR is not specified, OUTPUT_DIR is set to INPUT_DIR.

requirements
----------------------------------

* python2.4 or above(2.x)

* ExifTool

  Install OSX Package. Download from http://www.sno.phy.queensu.ca/~phil/exiftool/index.html

* FFMpeg

  Install your own ffmpeg onto /usr/local/bin/ffmpeg.
  
  or Install ClipGrab. Download from http://clipgrab.de/start_en.html

License
----------------------------------
New BSD License

Copyright 2010- tsuyukimakoto
"""

import time
from datetime import datetime
import subprocess
import os
import glob
import sys
import re

dt_r = re.compile(r'.*(?P<year>\d{4}):(?P<month>\d{2}):(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})')

EXIFTOOL = '/usr/bin/exiftool'

FFMPEG = '/Applications/ClipGrab.app/Contents/MacOS/ffmpeg'
OWN_FFMPEG = '/usr/local/bin/ffmpeg'
if os.path.exists(OWN_FFMPEG):
  FFMPEG = OWN_FFMPEG

def do_it(cmd):
  p = subprocess.Popen(cmd, shell=True, cwd='/', stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       close_fds=True)
  (stdouterr, stdin) = (p.stdout, p.stdin)
  output = []
  while True:
    line = stdouterr.readline()
    if not line:
      break
    output.append(line)
  ret = p.wait()
  return (ret, '\n'.join(output))

def utc_datetime_original(target_file):
  cmd = ' '.join((EXIFTOOL, '-DateTimeOriginal', target_file,))
  (result, output) = do_it(cmd) # Date/Time Original              : 2010:10:30 16:16:16+09:00
  if len(output) > 0:
    m = dt_r.match(output)
    if m:
      d = datetime.fromtimestamp(
                      time.mktime(
                          datetime(
                            int(m.group('year')),
                            int(m.group('month')),
                            int(m.group('day')),
                            int(m.group('hour')),
                            int(m.group('minute')),
                            int(m.group('second'))
                          ).timetuple()
                        )
                      )
      return d
  return None

def main(target_dir, output_dir):
  target_dir = sys.argv[1]
  target_files = glob.glob(os.path.join(target_dir, '*.MTS'))
  for target_file in target_files:
    file_name = os.path.split(target_file)[1]
    output_file = os.path.join(output_dir,os.path.splitext(file_name)[0] + '.m4v')
    target_file = os.path.join(target_dir, target_file)
    print '%s to %s' % (target_file, output_file)
    if not os.path.exists(output_file):
      cmd_list = [FFMPEG, '-i', target_file, '-vcodec', 'copy', '-acodec', 'copy', '-ac', '6']
      #cmd_list = [FFMPEG, '-i', target_file, '-vcodec', 'copy', '-acodec', 'libfaac', '-ac', '6']
      create_date = utc_datetime_original(target_file)
      t = None
      if create_date:
        cmd_list.append('-timestamp')
        cmd_list.append('"%04d-%02d-%02d %02d:%02d:%02d"' % (create_date.year,
                                                           create_date.month,
                                                           create_date.day,
                                                           create_date.hour,
                                                           create_date.minute,
                                                           create_date.second,
                                                           ))
        t = time.mktime(create_date.timetuple())
      cmd_list.append(output_file)
      (result, output) = do_it(' '.join(cmd_list))
      if t:
        os.utime(output_file, (t, t))

if __name__ == '__main__':
  if not os.path.exists(FFMPEG):
    print 'You must install ffmpeg onto /usr/local/bin/ffmpeg or install ClipGrab.'
    quit()
  if not os.path.exists(EXIFTOOL):
    print 'You must install ExifTool.'
    quit()
  if len(sys.argv) < 2:
    print 'You must specify target directory.'
    quit()
  if not os.path.isdir(sys.argv[1]):
    print 'You must specify target directory.'
    quit()
  output_dir = sys.argv[1]
  if len(sys.argv) == 3:
    output_dir = sys.argv[2]
  main(sys.argv[1], output_dir)

