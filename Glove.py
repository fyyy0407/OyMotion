import asyncio
import os
import signal
import sys
import time
import math

from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient

from lib_gforce import gforce
from lib_gforce.gforce import EmgRawDataConfig, SampleResolution

from roh_registers_v1 import *


class Glove:
    """
    API for glove

    Args:
    DEV_NAME_PREFIX,DEV_MIN_RSSI: Device filters
    SAMPLE_RESOLUTION: 8 or 12
    INDEX_CHANNELS: Channel0: thumb, Channel1: index, Channel2: middle, Channel3: ring, Channel4: pinky, Channel5: thumb root
    """

    def __init__(self,DEV_NAME_PREFIX = "",DEV_MIN_RSSI = -128,SAMPLE_RESOLUTION = 8, batch_len = 48, fs = 300,NUM_FINGERS = 6,INDEX_CHANNELS = [7, 6, 0, 3, 4, 5]):
        super(Glove,self).__init__()
        signal.signal(signal.SIGINT, lambda signal, frame: self._signal_handler())
        self.SAMPLE_RESOLUTION = SAMPLE_RESOLUTION
        self.fs = fs
        self.NUM_FINGERS = NUM_FINGERS
        self.INDEX_CHANNELS = INDEX_CHANNELS
        self.batch_len = batch_len
        self.terminated = False
        self.gforce_device = gforce.GForce(DEV_NAME_PREFIX, DEV_MIN_RSSI)
        self.emg_data = [0 for _ in range(NUM_FINGERS)]
        self.emg_min = [0 for _ in range(NUM_FINGERS)]
        self.emg_max = [0 for _ in range(NUM_FINGERS)]
        self.finger_data = [0 for _ in range(NUM_FINGERS)]
        self.q = asyncio.Queue() 
    
    async def connect_gforce_device(self):
        '''
        connect gloves
        '''
        try:
            await self.gforce_device.connect()
        except Exception as e:
            print(e)

        
        if self.gforce_device.client == None or not self.gforce_device.client.is_connected:
            exit(-1)
        
        print("Connected to {0}".format(self.gforce_device.device_name))
        
        # Set the EMG raw data configuration, default configuration is 8 bits, 16 batch_len
        if self.SAMPLE_RESOLUTION == 12:
            sr = SampleResolution.BITS_12
        else:
            sr = SampleResolution.BITS_8

        cfg = EmgRawDataConfig(fs = self.fs, channel_mask=0xff, batch_len = self.batch_len, resolution = sr)
        await self.gforce_device.set_emg_raw_data_config(cfg)

        baterry_level = await self.gforce_device.get_battery_level()
        print("Device baterry level: {0}%".format(baterry_level))
        
        await self.gforce_device.set_subscription(gforce.DataSubscription.EMG_RAW)
        self.q = await self.gforce_device.start_streaming()

    async def calib(self,flag):     
        '''
        Calib for fingers range
        Args:
            flag = true requires calib, otherwise set to default values
        '''
        
        if flag==False:
            self.emg_min = [32,24,24,24,24,30]
            self.emg_max = [34,52,52,52,52,40]

        input("Please spread your fingers")
        for _ in range(256):
            v = await self.q.get()
            for i in range(len(v)):
                for j in range(self.NUM_FINGERS):
                    self.emg_max[j] = round((self.emg_max[j]+v[i][self.INDEX_CHANNELS[j]])/2 )

        input("Please rotate your thumb root to maximum angle")

        for _ in range(256):
            v = await self.q.get()
            for i in range(len(v)):
                self.emg_min[5] = round((self.emg_min[5]+v[i][self.INDEX_CHANNELS[5]])/2 )

        input("Please make a fist")

        for _ in range(256):
            v = await self.q.get()
            for i in range(len(v)):
                for j in range(self.NUM_FINGERS - 1):
                    self.emg_min[j] = round((self.emg_min[j]+v[i][self.INDEX_CHANNELS[j]])/2)
        
        range_valid = True

        for i in range(self.NUM_FINGERS):
            print("MIN/MAX of finger {0}: {1}-{2}".format(i, self.emg_min[i], self.emg_max[i]))
            if (self.emg_min[i] >= self.emg_max[i]):
                range_valid = False

        if not range_valid:
            print("Invalid range(s), exit.")
            exit(-1)

    @staticmethod
    def clamp(n, smallest, largest):
        return max(smallest, min(n, largest))
    
    @staticmethod
    def _signal_handler(self):
        print("You pressed ctrl-c, exit")
        self.terminated = True
        
    @staticmethod
    def interpolate(n, from_min, from_max, to_min, to_max):
        return (n - from_min) / (from_max - from_min) * (to_max - to_min) + to_min
    
    async def get_pos(self):
        v = await self.q.get()

        for i in range(len(v)):
            self.emg_data[j] = round((self.emg_data[j] + v[i][self.INDEX_CHANNELS[j]]) / 2)
            self.finger_data[j] = round(self.interpolate(self.emg_data[j], self.emg_min[j], self.emg_max[j], 65535, 0))
            self.finger_data[j] = self.clamp(self.finger_data[j], 0, 65535)
    