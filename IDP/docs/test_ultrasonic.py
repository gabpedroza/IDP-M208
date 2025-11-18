from machine import ADC, Pin
from time import sleep
adc = ADC(Pin(28))     # create ADC object on GP number

#works for up to 40cm and no less than 5cm.
#unable to detect boxes in testing. We will use this as the RIGHT sensor for now
while True:
    msum = 0
    for _ in range(1):
        msum += adc.read_u16()*390/65535 #12-bit ADC
        #390 seems to give accurate numbers 
        sleep(0.04) #below the 30 Hz max polling rate
    print(msum/1)