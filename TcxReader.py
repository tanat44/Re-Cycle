import xml.etree.ElementTree as ET
import dateutil.parser

class TcxReader:
    def parse(filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        namespace = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}'

        trackPoints = []

        for trackPoint in root.findall('.//' + namespace + 'Trackpoint'):
            tp = {}
            for child in trackPoint:
                
                if child.tag == namespace + 'Time':
                    tp['time'] = dateutil.parser.isoparse(child.text)

                if child.tag == namespace + 'Position':
                    for x in child:
                        if x.tag == namespace + 'LatitudeDegrees':
                            tp['latitude'] = float(x.text)
                        if x.tag == namespace + 'LongitudeDegrees':
                            tp['longtitude'] = float(x.text)

                if child.tag == namespace + 'Extensions':
                    tp['speed'] = float(child[0][0].text)

            trackPoints.append(tp)

        # post processing
        startTime = trackPoints[0]['time']    
        for tp in trackPoints:
            tp['time'] = (tp['time']-startTime).total_seconds()

        return trackPoints
