class TrackPoint:
    def __init__(self, data):
        self.data = data
        self.lastFindTimeIndex = 0

    def offsetTime(self, offset):
        if offset > 0:
            while len(self.data) > 0:
                if self.data[0]['time'] < offset:
                    self.data.pop(0)
                else: 
                    break

            startTime = self.data[0]['time']
            for t in self.data:
                t['time'] -= startTime
            
        # padd the front with the first track
        else:
            track0 = self.data[0]
            track0['speed'] = 0
            for i in range (1, offset):
                self.data.insert(track0, 0)

    def estimateSpeed(self, time):
        previousIndex = -1

        space = range(self.lastFindTimeIndex, len(self.data) - 1)
        for i in space:
            if self.data[i]['time'] > time:
                self.lastFindTimeIndex = i-1
                break

        # linear interpolation
        speed = 0
        if self.lastFindTimeIndex < len(self.data):
            v0 = self.data[self.lastFindTimeIndex]['speed']
            v1 = self.data[self.lastFindTimeIndex + 1]['speed']
            dv = v1 - v0
            dt = time - self.data[self.lastFindTimeIndex]['time']
            duration = self.data[self.lastFindTimeIndex + 1]['time'] - self.data[self.lastFindTimeIndex]['time']
            speed = v0 + float(dt / duration)*dv
      
        return speed


    
