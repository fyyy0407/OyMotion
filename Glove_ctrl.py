import asyncio
import os
import signal
import sys
import time

from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient

from lib_gforce import gforce
from lib_gforce.gforce import EmgRawDataConfig, SampleResolution

from roh_registers_v1 import *



class GloveCtrl:
    """
    API for glove control

    Args:
    COM_PORT,NODE_ID,NUM_FINGERS: ROHand Configuration
    DEV_NAME_PREFIX,DEV_MIN_RSSI: Device filters
    SAMPLE_RESOLUTION: 8 or 12
    INDEX_CHANNELS: Channel0: thumb, Channel1: index, Channel2: middle, Channel3: ring, Channel4: pinky, Channel5: thumb root
    """

    def __init__(self,COM_PORT="/dev/ttyUSB0",NODE_ID=2,NUM_FINGERS=6,DEV_NAME_PREFIX = "",DEV_MIN_RSSI = -128,SAMPLE_RESOLUTION = 12,INDEX_CHANNELS = [7, 6, 0, 3, 4, 5]):
        super(GloveCtrl,self).__init__()
        signal.signal(signal.SIGINT, lambda signal, frame: self._signal_handler())
        self.terminated = False
        self.gforce_device = gforce.GForce(DEV_NAME_PREFIX, DEV_MIN_RSSI)
        self.emg_data = [0 for _ in range(NUM_FINGERS)]
        self.emg_min = [0 for _ in range(NUM_FINGERS)]
        self.emg_max = [0 for _ in range(NUM_FINGERS)]
        self.prev_finger_data = [65535 for _ in range(NUM_FINGERS)]
        self.finger_data = [0 for _ in range(NUM_FINGERS)]
        self.client =  ModbusSerialClient(COM_PORT, FramerType.RTU, 115200)
        self.client.connect()

        try:
            await self.gforce_device.connect()
        except Exception as e:
            print(e)

        if gforce_device.client == None or not gforce_device.client.is_connected:
            exit(-1)

        print("Connected to {0}".format(gforce_device.device_name))

        
    def clamp(n, smallest, largest):
        return max(smallest, min(n, largest))

    def _signal_handler(self):
        print("You pressed ctrl-c, exit")
        self.terminated = True

    def interpolate(n, from_min, from_max, to_min, to_max):
        return (n - from_min) / (from_max - from_min) * (to_max - to_min) + to_min



