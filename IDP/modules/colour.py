from machine import Pin, I2C
import time
import math

# TCS34725 I2C address
TCS34725_ADDR = 0x29
COMMAND_BIT = 0x80

# Register addresses
REG_ENABLE = 0x00
REG_ATIME = 0x01
REG_CONTROL = 0x0F
REG_ID = 0x12
REG_CDATAL = 0x14  # Clear channel data low byte
REG_RDATAL = 0x16
REG_GDATAL = 0x18
REG_BDATAL = 0x1A

# Enable register bits
ENABLE_AEN = 0x02  # RGBC enable
ENABLE_PON = 0x01  # Power ON

class ColourSensor:
    def __init__(self, i2c, enable_pin, integration_time=0xEB, gain=0x01):
        self.enable_pin = Pin(enable_pin, mode=Pin.OUT)
        self.i2c = i2c
        self.integration_time = integration_time
        self.gain = gain

        # Check sensor ID
        sensor_id = self._read8(REG_ID)
        if sensor_id not in (0x44, 0x10):
            raise RuntimeError("TCS34725 not found or wrong ID: 0x{:02X}".format(sensor_id))

        # Set integration time and gain
        self._write8(REG_ATIME, self.integration_time)
        self._write8(REG_CONTROL, self.gain)

        #do not enable yet

    def enable(self):
        self.enable_pin.high()
        time.sleep_ms(3)
        self._write8(REG_ENABLE, ENABLE_PON)
        time.sleep_ms(3)
        self._write8(REG_ENABLE, ENABLE_PON | ENABLE_AEN)

    def disable(self):
        reg = self._read8(REG_ENABLE)
        self._write8(REG_ENABLE, reg & ~(ENABLE_PON | ENABLE_AEN))
        self.enable_pin.low()

    def _read8(self, reg):
        return self.i2c.readfrom_mem(TCS34725_ADDR, COMMAND_BIT | reg, 1)[0]

    def _read16(self, reg):
        data = self.i2c.readfrom_mem(TCS34725_ADDR, COMMAND_BIT | reg, 2)
        return data[1] << 8 | data[0]

    def _write8(self, reg, value):
        self.i2c.writeto_mem(TCS34725_ADDR, COMMAND_BIT | reg, bytes([value]))

    def read_raw(self):
        """Returns raw (red, green, blue) values."""
        red = self._read16(REG_RDATAL)
        green = self._read16(REG_GDATAL)
        blue = self._read16(REG_BDATAL)
        return red, green, blue
    
    def sample(self, thresh=200, sample_time=1) -> str:
        '''read for sample_time seconds and return most likely colour based on averaging.'''
        #enable the sensor
        self.enable()
        time.sleep_ms(3)
        
        #sample for 1 second
        reds = []
        greens = []
        blues = []
        t_end = time.time() + sample_time
        while time.time() < t_end:
            red, green, blue = sensor.read_raw() #take sample
            
            #add to respective colour lists
            reds.append(red)
            greens.append(green)
            blues.append(blue)
        
        #now average all
        red_tot = 0
        for sample in reds:
            red_tot += sample
        red_ave = red_tot / len(reds)

        blue_tot = 0
        for sample in blues:
            blue_tot += sample
        blue_ave = blue_tot / len(blues)
        
        green_tot = 0
        for sample in greens:
            green_tot += sample
        green_ave = green_tot / len(blues)

        averages = (red_ave, green_ave, blue_ave)
        print(averages)

        #filter by thresh. if nothing left, return early
        filtered_averages = [x for x in averages if (x>thresh)]
        if len(filtered_averages) == 0:
            self.disable()
            return 'unknown'

        #now decide intensity of most likely colour 
        best = max(filtered_averages)

        #find index in original set
        for i in range(len(averages)):
            if averages[i] == best:
                colour_index = i
                break

        #map back to colours
        if colour_index == 0:
            self.disable()
            return 'red'
        elif colour_index == 1:
            self.disable()
            return 'green'
        elif colour_index == 2:
            self.disable()
            return 'blue'
        else:
            self.disable()
            return 'unknown'

        


# -------------------------
# Test
# -------------------------
try:
    # Initialize I2C (adjust pins for your board)
    enabler = Pin(22, Pin.OUT)
    enabler.high()
    time.sleep_ms(3)
    i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
    sensor = ColourSensor(i2c, enable_pin=22)
    enabler.low()


    while True:
        colour = sensor.sample()

        print(f'colour:{colour}\n')
        time.sleep(1)

except Exception as e:
    print("Error:", e)


#blue typicals: (262.7201, 1067.307, 2565.012)
#red typicals: (664.3676, 381.8382, 552.3268)
#green typicals: (152.4273, 294.4619, 356.7753)
#yellow typicals: (1330.29, 1871.378, 970.4729)