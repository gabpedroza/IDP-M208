## Sensors
### I2C ports testing
Using the very reliable VL53L0X, all I2C pin pairs (not connected to motors) were tested. All of them work, besides:
- Pins 31 & 32 (GP 26 & GP 27) don't seem to work. The sensor spits an error:
```
Traceback (most recent call last):
  File "<stdin>", line 33, in <module>
  File "<stdin>", line 11, in test_vl53l0x
  File "libs/VL53L0X/VL53L0X.py", line 114, in __init__
  File "libs/VL53L0X/VL53L0X.py", line 164, in init
  File "libs/VL53L0X/VL53L0X.py", line 149, in _flag
  File "libs/VL53L0X/VL53L0X.py", line 145, in _register
  File "libs/VL53L0X/VL53L0X.py", line 137, in _registers
OSError: [Errno 110] ETIMEDOUT
```

Since both I2C channels seem to work, this shouldn't be a problem.

`TODO`: check if pins 31 & 32 work with other sensors.
### VL53L0X ToF distance sensor
It works out of the box. The I2C address is 0x29, which conflicts with TCS3462S. Hence it is a good strategy to turn off the colour sensor when it's not in use.

The sensor seems to have a constant offset of about 25mm (that is, the real distance is generally 25mm less than it detects), but is otherwise more accurate than my measurements. It can detect distances reliably from 4cm all the way to about 17.5cm, assuming its offset is consistent (which seemed very likely).
### TCS3472S colour sensor
It needs pull-up resistors on SDA (green) and SCL; $\mathrm{10k}\Omega$ works. Its address is 0x29 (you can tell the pull up is not working if the Pico picks up an address that is not 0x29 = 41).

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
`TODO`: tests other pull up values, test colour range with the proper blocks.
### TTL line sensors
They are plug and play. They require pull-down resistors, which the Pico can supply internally (`Pin(#pin_number#, Pin.IN, Pin.PULL_DOWN)` from the handout).

They (number is at the moment codified by the number of knots on their wires) were measured to have the following characteristics (distances measured from the PCB):

1. TTL #1 could detect the back of the breadboard from a 2.7cm distance.
2. TTL #2 could detect the back of the breadboard from a 2.9cm distance.
3. TTL #3 could detect the back of the breadboard from a 2.65cm distance.
4. TTL #4 could detect the back of the breadboard from a 2.8cm distance.

The sensors light up with a blue LED on their back when they see something white. This could potentially be useful when diagnosing robot problems.
### TMF8701 Distance sensor
It works out of the box, with I2C address 65.

It has three sensing modes: proximity, distance, and combine. It also supports built-in calibration. 

1. In the proximity mode, the sensor can only detect object up to 9cm from it. It was most accurate around the 5cm mark, and it was found it doesn't have a constant offset (though it didn't deviate by more than 7mm). It could detect objects within that accuracy all the way to basically touching the sensor.

2. In the distance mode, it could detect objects up to about 17cm away. Again, the offset seemed to shift with distance, and it seemed most accurate at the 8cm mark. The offset could vary my more than 1.5cm. It could detect objects well up to touching distance.

3. In the hybrid (combined) mode, it seemed to be no better than the distance mode. 8cm mark looked accurate, but it had varying offset elsewhere. The range seems to be longer than the proximity mode, but shorter than the distance mode.

`TODO`: discover how to use the calibration feature.

### Ultrasonic sensor
The sensor is plug and play, but must be connected to a port with ADC. Adapting the code from [here](https://docs.micropython.org/en/latest/rp2/quickref.html) and [here](https://wiki.dfrobot.com/URM09_Ultrasonic_Sensor_(Gravity_Analog)_SKU_SEN0307), it can thus be written:
```python
from machine import ADC, Pin
from time import sleep
adc = ADC(Pin(28))     # create ADC object on GP number
        
while True:
    msum = 0
    for _ in range(10):
        msum += adc.read_u16()*390/65535 #12-bit ADC
        #390 seems to give accurate numbers 
        sleep(0.04) #below the 30 Hz max polling rate
    print(msum/10)

```
The sensor fluctuates a lot and very drastically between measurements (e.g. by 3cm). By averaging e.g. the last 10 measurements as above, the sensor still has acceptable throughput and is much more stable. 

Since it behaves in such a simple way, the error is strongly dependent on the multiplying constant chosen. `390` gives about half a centimeter of error from 4cm all the way to 24cm. This can be made better with finer tuning.
## LED circuit Biasing
### Red LED with BJT
- Pulldown resistor 10k between emitter and input
- 2.7k resistor at base
- 150Ohm resistor at drain