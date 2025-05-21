# Micropython DHT driver
# Based on code from: https://github.com/micropython/micropython/blob/master/drivers/dht/dht.py

import time
from machine import Pin

class DHTBase:
    def __init__(self, pin):
        self.pin = pin
        self.pin.init(Pin.OUT, Pin.PULL_UP)

    def _read(self):
        self.pin.init(Pin.OUT, Pin.PULL_UP)
        self.pin.value(0)
        time.sleep_ms(18)
        self.pin.init(Pin.IN, Pin.PULL_UP)
        time.sleep_us(40)

        buf = bytearray(5)
        for i in range(5):
            val = 0
            for j in range(8):
                while self.pin.value() == 0:
                    pass
                t = time.time_ns()
                while self.pin.value() == 1:
                    pass
                if time.time_ns() - t > 50000: # 50us
                    val = (val << 1) | 1
                else:
                    val = (val << 1) | 0
            buf[i] = val

        if (buf[0] + buf[1] + buf[2] + buf[3]) & 0xFF != buf[4]:
            raise Exception("checksum error")
        return buf

class DHT11(DHTBase):
    def __init__(self, pin):
        super().__init__(pin)
        self.__temperature = -1
        self.__humidity = -1

    def measure(self):
        buf = self._read()
        self.__humidity = buf[0] + buf[1] / 10.0
        self.__temperature = buf[2] + buf[3] / 10.0

    def temperature(self):
        return self.__temperature

    def humidity(self):
        return self.__humidity