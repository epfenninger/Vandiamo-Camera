#!/usr/bin/env python3
import gi 
import sys
from time import sleep
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
from datetime import datetime
import os

Gst.init(sys.argv)

dashcamString = 'v4l2src device=/dev/v4l/by-id/usb-MACROSIL_AV_TO_USB2.0-video-index0 do-timestamp=true pixel-aspect-ratio=1 norm=NTSC ! video/x-raw, format=(string)YUY2, width=(int)720, height=(int)480, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1 ! nvvidconv ! clockoverlay halignment=left valignment=bottom text=Rear$

def main():
  while(True):
    now = datetime.now()
    curTimeString=str(now.time().strftime("%H-%M-%S"))
    curDateString = str(now.date())

    path = "/home/epfenninger/NVR/Clips/Rearcam/"+curDateString+"/" 
    
    if(not os.path.isdir(path)):
      print("Date folder doesn't exist, creating")
      os.mkdir(path)
    else:
      print("Folder exists, continuing")
    
    filename = path+"Rearcam+"+curTimeString
    pipeline = Gst.parse_launch(dashcamString+filename+".mkv")
    start = datetime.now()
    bus = pipeline.get_bus() 
    try:        
      pipeline.set_state(Gst.State.PLAYING)
    except Exception as e:
      return 1
      break

    print('Recording Rearcam')
    while ((divmod((now - start).total_seconds(),60)[0]) < 15):
      sleep(30)
      now = datetime.now()
    print('Sending EOS')
    pipeline.send_event(Gst.Event.new_eos())
    print('Waiting for EOS')
    bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.EOS)
    pipeline.set_state(Gst.State.NULL)

    return 0

rebootCounter = 0
while(True):
  exitCode = main()

  if (rebootCounter > 9):
    os.system('reboot')

  if (exitCode == 1):
    sleep(60)
    print('Gstreamer having issues, waiting a minute')
    rebootCounter = rebootCounter + 5
    
  if (exitCode == 0):
    sleep(5)
    rebootCounter = rebootCounter + 1
