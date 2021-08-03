from PyQt6.QtCore import QCoreApplication, QTimer, Qt
from PyQt6.QtWidgets import QMessageBox
from pcr.hid_ctrl import Hid_manager
from pcr.hid_action import TxAction, RxAction
from pcr.constant import Command, State, State_Oper, DeviceConstant

import time
import hid
import sys

class PCR_Timer:
    TIMER_DURATION = 100 #100ms
    def __init__(self, pcr_task):
        self.task = pcr_task
        
        #Hid class
        try:
            self.hid = Hid_manager(vender_id = DeviceConstant.VENDOR_ID, product_id = DeviceConstant.PRODUCT_ID)
        except hid.HIDException as err:
            QMessageBox.critical(self.task.mainUI, 'Hid Error', 'USB 커넥터를 확인한 뒤 재실행 부탁드립니다')
            #QCoreApplication.instance().quit()
            sys.exit()

        #Tx_buffer
        self.tx_action = TxAction()

        #Timer
        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setInterval(PCR_Timer.TIMER_DURATION) #set interval
        self.timer.timeout.connect(self.run) #connect run() to timer

        self.start_time = 0
        self.end_time = 0

    def read_buffer(self):

        try:
            rx_buffer = self.hid.read()
            self.end_time = time.time()
        except hid.HIDException as err:
            QMessageBox.critical(self.task.mainUI, 'Hid Error', 'USB 커넥터를 확인하세요')
            #QCoreApplication.instance().quit()
            sys.exit()

        if rx_buffer: 
            self.task.rx_action.set_info(rx_buffer) #Set info
            self.task.state = self.task.rx_action['State'] #Set state
        else: #if get rx_buffer nothing
            pass
            #print("NOTHING...")

    def send_buffer(self):
        command = self.task.command

        if command == Command.NOP:
            #Write Tx buffer
            tx_buffer = self.tx_action.tx_NOP()

        elif command == Command.TASK_WRITE:
            tx_buffer = self.tx_action.tx_taskWrite(self.task.protocol[self.task.protocol_ind],
                                                    self.task.preheat,
                                                    self.task.protocol_ind)
            
        elif command == Command.TASK_END:
            tx_buffer = self.tx_action.tx_taskEnd()
            self.isTaskEnd = True

        elif command == Command.GO:
            tx_buffer = self.tx_action.tx_go()
        
        elif command == Command.STOP:
            self.running = False
            self._stop = False
            
            tx_buffer = self.tx_action.tx_stop()

        try:
            self.start_time = time.time()
            self.hid.write(tx_buffer)
        except hid.HIDException as err:
            QMessageBox.critical(self.task.mainUI, 'Hid Error', 'USB 커넥터를 확인하세요')
            #QCoreApplication.instance().quit()
            sys.exit()

    def run(self):
        # read buffer
        self.read_buffer()

        # check status
        self.task.check_status()

        # calc temperature
        self.task.calc_temp()

        # line task
        self.task.line_task()

        # get device protocol
        self.task.get_device_protocol()

        # error check
        self.task.error_check()

        # calc time
        self.task.calc_time()

        # set command
        self.task.set_command()
        
        # send buffer
        self.send_buffer()

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

#timer = PCR_Timer()