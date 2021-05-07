import matplotlib.pyplot as plt
import time
import numpy as np
from threading import Thread

class SpeedPlotter:
    def __init__(self, trackPoints):
        self.thread = Thread(target=self.plot, args=())
        self.time = 0

        self.x = []
        self.y = []
        for trackpoint in trackPoints:
            self.x.append(trackpoint['time'])
            self.y.append(trackpoint['speed'] * 18.0 /5)

        self.running = True
        self.thread.start()


    def start(self):
        self.thread.start()

    def updateTime(self, time):
        self.time = time

    def plot(self):
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        line1, = ax.plot(self.x, self.y, 'k-') 
        line2, = ax.plot([0,0], [0,99], 'r-') 

        while self.running:
            line2.set_xdata([self.time,self.time])
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.5)

        self.thread.join()
