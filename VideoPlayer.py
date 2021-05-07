# MULTI_THREADING REPLAY VIDEO ON OPENCV MATCHING ORIGINAL FPS

from imutils.video import FPS
from imutils.video import FileVideoStream
import numpy as np
import argparse
import imutils
import cv2
from threading import Thread
from queue import Queue
import time
from enum import Enum

OUTPUT_FPS = 30
OUTPUT_FRAME_DURATION = 1000 / OUTPUT_FPS

def getTimeMs():
    return time.time() * 1000

class Mode(Enum):
    FREERUN = 1
    TRIGGER = 2
    SPEEDCONTROL = 3
    SYNCTRACKPOINT = 4


class VideoPlayer:
    def __init__(self, filename, mode = Mode.FREERUN, trackPoint = None):
        self.fvs = FileVideoStream(filename, queue_size=700).start()
        self.fps = FPS()
        self.mode = mode

        self.fpsOriginal = self.fvs.stream.get(cv2.CAP_PROP_FPS)
        self.frameDuration = float(1000) / self.fpsOriginal
        self.frameNo = 0
        self.startTime = 0
        print("FPS ORIGINAL IS", self.fpsOriginal, self.frameDuration)

        if mode == Mode.FREERUN:
            self.thread = Thread(target=self.play, args=())
        elif mode == Mode.TRIGGER:
            self.thread = Thread(target=self.playFrame, args=())
        elif mode == Mode.SPEEDCONTROL:
            self.thread = Thread(target=self.playSpeedControl, args=())
        elif mode == Mode.SYNCTRACKPOINT:
            self.thread = Thread(target=self.playSyncTrackPoint, args=())

        self.triggerOn = False
        self.running = True
        self.targetSpeed = 0
        self.keyFrame = -1
        self.trackPoint = trackPoint
        self.frameError = 0
        self.frameSinceSetSpeed = 0

        self.callbackFrame = None

    def start(self):
        self.fps.start()
        self.startTime = getTimeMs()
        self.thread.start()
        

    def stop(self):
        print("video player stop")
        self.running = False
        self.thread.join()
        

    def play(self):
        while self.fvs.more() and self.running:

            frame = self.fvs.read()
            if frame is None:
                break
            cv2.putText(frame, "Queue Size: {}".format(self.fvs.Q.qsize()),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
            cv2.imshow("Frame", frame)
            self.frameNo += 1
            videoTime = self.frameNo * self.frameDuration
            duration = getTimeMs() - self.startTime
            diff = int(videoTime - duration)
            waitTime = 1
            if diff > 0:
                waitTime = diff
            key = cv2.waitKey(waitTime)
            if key == ord('q'):
                break
            if self.callbackFrame is not None:
                self.callbackFrame(duration/1000)
            self.fps.update()

        self.endPlay()

    
    def playSpeedControl(self):
        originalClipSpeed = 5.5 #m/s
        while self.fvs.more() and self.running:

            frame = self.fvs.read()
            if frame is None:
                break
            cv2.putText(frame, "Queue Size: {}".format(self.fvs.Q.qsize()),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)	
            cv2.putText(frame, "Speed: {}km/h".format(int(self.targetSpeed * 18.0 / 5)),(10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)	
            cv2.imshow("Frame", frame)
            self.frameNo += 1

            quit = False
            while self.targetSpeed < 0.1:
                key = cv2.waitKey(100)
                if key == ord('q'):
                    quit = True
                    break
            if quit:
                break
            

            speedFactor = self.targetSpeed / originalClipSpeed
            newFps = self.fpsOriginal * speedFactor
            newDuration = float(1000) /  newFps

            videoTime = (self.frameNo - self.keyFrame) * newDuration
            duration = getTimeMs() - self.startTime
            diff = int(videoTime - duration)
            waitTime = 1
            if diff > 0:
                waitTime = diff
            key = cv2.waitKey(waitTime)
            if key == ord('q'):
                break

            self.fps.update()

        self.endPlay()

    def playSyncTrackPoint(self):

        while self.fvs.more() and self.running:

            # handle very slow targetSpeed
            quit = False
            while self.targetSpeed < 0.1:
                key = cv2.waitKey(100)
                if key == ord('q'):
                    quit = True
                    break
            if quit:
                break

            clipSpeed = self.trackPoint.estimateSpeed( float(self.frameNo) / self.fpsOriginal )
            if clipSpeed < 0.1:
                clipSpeed = 0.1            
            speedFactor = self.targetSpeed / clipSpeed
            waitTime = 1
            frame = None

            #skip frame to match targetSpeed
            if speedFactor > 1:
                realError = speedFactor + self.frameError
                skipFrames = int(realError)
                self.frameError = realError - skipFrames
                for i in range(skipFrames-1):
                    self.fvs.read()

                frame = self.fvs.read()
                self.frameNo += skipFrames
                self.frameSinceSetSpeed += 1

                # find waitTime
                actualElapse = getTimeMs() - self.startTime
                displayTime = OUTPUT_FRAME_DURATION * self.frameSinceSetSpeed
                if actualElapse < displayTime:
                    waitTime = displayTime - actualElapse

            # slow frame to match targetSpeed
            else:
                frame = self.fvs.read()
                self.frameNo += 1
                waitTime = OUTPUT_FRAME_DURATION / speedFactor
                self.frameSinceSetSpeed += 1.0/speedFactor


            # draw
            fps = (getTimeMs() - self.startTime) / self.frameSinceSetSpeed
            cv2.putText(frame, "Queue Size: {}".format(self.fvs.Q.qsize()),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)	
            cv2.putText(frame, "Speed: {}km/h".format(int(self.targetSpeed * 18.0 / 5)),(10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)	
            cv2.putText(frame, "FPS: {:.2f}".format(fps) ,(10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)	
            if frame is None:
                break
            cv2.imshow("Frame", frame)            

            # wait to match target FPS
            key = cv2.waitKey(int(waitTime))
            if key == ord('q'):
                break

            self.fps.update()

        self.endPlay()

    def setSpeed(self, speed):    # speed in m/s
        self.targetSpeed = speed
        self.keyFrame = self.frameNo
        self.startTime = getTimeMs()
        self.frameSinceSetSpeed = 0

    def trigger(self):
        self.triggerOn = True


    def playFrame(self):
        while self.fvs.more() and self.running:

            while not self.triggerOn and self.running:
                time.sleep(0.1)

            frame = self.fvs.read()
            if frame is None:
                break
            cv2.putText(frame, "Queue Size: {}".format(self.fvs.Q.qsize()),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
            cv2.imshow("Frame", frame)
            self.frameNo += 1
            self.triggerOn = False
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            self.fps.update()

        self.endPlay()

    def endPlay(self):
        self.fps.stop()
        print("total frames", self.frameNo)
        print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
        # do a bit of cleanup
        cv2.destroyAllWindows()
        self.fvs.stop()

    def setCallbackFrame(self, f):
        self.callbackFrame = f