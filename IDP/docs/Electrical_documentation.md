## Sensors
### TCS3472S colour sensor
It needs pull-up resistors on SDA and SCL; $\mathrm{10k}\Omega$ works. Its address is 0x29 (you can tell the pull up is not working if the Pico picks up an address that is not 0x29 = 41).

The sensor was extremely volatile as tested. The numbers were stable, but it would recurrently disconnect from I2C, hence, a fault-tolerant code is needed, e.g. (adapted from handout):

```python
from machine import Pin, SoftI2C, I2C
from libs.tcs3472_micropython.tcs3472 import tcs3472
from utime import sleep

def test_tcs3472():
    i2c_bus = I2C(id=0, sda=Pin(8), scl=Pin(9)) 
    tcs = tcs3472(i2c_bus)

    while True:
        try:
            print("Light:", tcs.light())
            print("RGB:", tcs.rgb())
            sleep(1)
        except:
            try:
                tcs = tcs3472(i2c_bus)
            except:
                sleep(1)


if __name__ == "__main__":
    test_tcs3472()
```
## LED circuit Biasing
### Red LED with BJT
- Pulldown resistor 10k between emitter and input
- 2.7k resistor at base
- 150Ohm resistor at drain