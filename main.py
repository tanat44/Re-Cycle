from VideoPlayer import VideoPlayer, Mode
from Server import ServerRunner
import time
import threading
from imutils.video import FPS
from TcxReader import TcxReader
from SpeedPlotter import SpeedPlotter
import matplotlib.pyplot as plt
from TrackPoint import TrackPoint

THRESHOLD = 500

# ENCODER PARAMETER
WHEEL_CIRCUMFERENCE = 2096 #mm
NO_ENCODER_SLIT = 2
ENCODER_FRAME_RATE = 0.5



if __name__ == "__main__":  

    tcx = TcxReader.parse(filename = '210506 chinatown-worachak-rachadamnoen.tcx')
    trackPoint = TrackPoint(tcx)
    trackPoint.offsetTime(34)
    # speedPlotter = SpeedPlotter(trackPoint.data)

    # def handleFrameUpdate(time):
    #     speedPlotter.updateTime(time)

    videoPlayer = VideoPlayer(filename = '210506 chinatown-worachak-rachadamnoen.mp4', mode=Mode.SYNCTRACKPOINT, trackPoint=trackPoint)
    # videoPlayer.setCallbackFrame(handleFrameUpdate)
    time.sleep(3)
    videoPlayer.start()
    videoPlayer.setSpeed(11.1)

    # def handleValue(value):
    #     speed = float(value) / NO_ENCODER_SLIT * WHEEL_CIRCUMFERENCE * ENCODER_FRAME_RATE / 1000
    #     print("value", value, "speed", speed, "km/h", speed*18/5)
    #     videoPlayer.setSpeed(speed)

    # server = ServerRunner(callbackValue = handleValue)

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("==== EXITING ====")
        # server.stopServer()
        videoPlayer.stop()