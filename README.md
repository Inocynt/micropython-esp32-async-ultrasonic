# micropython-esp32-async-ultrasonic
Utrasonic range measurement class for multiple HC-SR04 in MicroPython

# Example of usage
For 4 HC-SR04's connected to:
| Trigger pin | Echo pin |
| ----------- | -------- |
| 16 | 32|
| 17 | 33 |
| 18 | 34 |
| 19 | 35 |

```python
import time
from machine import Pin, Timer
from async_ultrasonic import AsyncUltrasonic

def start_measure():
    usg.measure()

def results(distances):
    print("{:>5.1f} {:>5.1f} {:>5.1f} {:>5.1f}".format(distances[0], distances[1], distances[2], distances[3]))
    time.sleep_ms(100)
    start_measure()

usg = AsyncUltrasonic(timer = Timer(0), triggerEchoPinPairs = [(Pin(16), Pin(32)), (Pin(17), Pin(33)), (Pin(18), Pin(34)), (Pin(19), Pin(35))], callback=results)


start_measure()
```
