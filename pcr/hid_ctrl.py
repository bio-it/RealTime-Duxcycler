from pcr.constant import Command, DeviceConstant
from pcr.hid_action import TxAction, RxAction
import time

# from pywinusb import hid
import hid
from ctypes import *

#To .dll
class Hid_manager(object):
    def __init__(self, vender_id = DeviceConstant.VENDOR_ID, product_id = DeviceConstant.PRODUCT_ID):
        self.hid = hid.Device(vender_id, product_id)
        self.manufacturer, self.serial = self.hid.manufacturer, self.hid.serial

        self.rx_buffer = []
        self.rx_action = RxAction()

    def __del__(self):
        self.hid.close()

    def read(self):
        #Rx_buffer_size : 65, Timeout : 1s
        self.rx_buffer = self.hid.read(65, 3)
        #self.rx_action.set_info(self.rx_buffer)
        return self.rx_buffer
        

    def write(self, buffer):
        self.hid.write(buffer)

    def get_action(self):
        return self.rx_action