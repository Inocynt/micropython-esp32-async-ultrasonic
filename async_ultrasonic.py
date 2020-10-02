from machine import Pin, PWM, Timer
import time
import micropython

class AsyncUltrasonic():
    def __init__(self, timer, triggerEchoPinPairs, callback):
        self.busy = False
        self.timer = timer
        self.resultsCallback = callback
        self.devices = triggerEchoPinPairs
        self.devicesCount = len(self.devices) 
        self.currentDevice = 0
        self._measureNextRef = self._measureNext
        self._initializeDevices()
        
    def _initializeDevices(self):
        self.echos = []
        for ix in range(self.devicesCount):
            self.echos.append({
                'start': 0,
                'end': 0
            })
            triggerPin, echoPin = self.devices[ix]
            triggerPin.init(Pin.OUT, None)
            triggerPin.off()
            echoPin.init(Pin.IN, Pin.PULL_DOWN)
            echoPin.irq(
                trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                handler=lambda pin, deviceIndex = ix: self._echoRead(pin, deviceIndex)
            );        

    def _echoRead(self, pin, index):
        if pin.value():
            self.echos[index]['start'] = time.ticks_us()
        elif self.echos[index]['end'] == 0:
            self.timer.deinit()
            self.echos[index]['end'] = time.ticks_us()
            micropython.schedule(self._measureNextRef, 0)
            
    def _echoTimeout(self):
        self.echos[self.currentDevice]['end'] = -1
        micropython.schedule(self._measureNextRef, 0)
        
    def _measureNext(self, _):
        self.currentDevice += 1
        if self.currentDevice >= self.devicesCount:
            self._measurmentFinished()
        else:
            self._startMeasurement()
            
    def _startMeasurement(self):
        triggerPin, echoPin = self.devices[self.currentDevice]
        self.timer.init(mode=Timer.ONE_SHOT, period=25, callback=lambda x: self._echoTimeout())
        triggerPin.on()
        time.sleep_us(10)
        triggerPin.off()
        
    def _measurmentFinished(self):
        distances = self._caclulcateDistances()
        self.busy = False
        micropython.schedule(self.resultsCallback, distances)
        
    def _caclulcateDistances(self):
        distances = []
        for echo in self.echos:
            distance = 200
            if echo['start'] > 0 and echo['end'] > echo['start']:
                distance = ((echo['end'] - echo['start']) * 34) / 2 / 1000
                if distance > 200: 
                    distance = 200
            distances.append(distance)
        return distances
    
    def _reset(self):
        self.currentDevice = 0
        for ix in range(self.devicesCount):
            self.echos[ix]['start'] = 0
            self.echos[ix]['end'] = 0
        
    def measure(self):
        if self.busy:
            raise Exception("Device not ready yet")
        self.busy = True
        self._reset()
        self._startMeasurement()
        
