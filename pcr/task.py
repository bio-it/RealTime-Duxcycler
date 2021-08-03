import time
import threading
import PyQt6
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QMessageBox 


from pcr.hid_action import TxAction, RxAction
from pcr.hid_ctrl import Hid_manager
from pcr.constant import Command, State, State_Oper, DeviceConstant
import pcr.protocol as Protocol
from pcr.timer import PCR_Timer

class PCR_Task:
    __instance = None
    
    @classmethod
    def _getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls.__instance

    def __init__(self, mainUI):
        super().__init__()

        #mainUI instance
        self.mainUI = mainUI

        #timer instance
        self.timer = None

        # state & command paramters
        self.state = State.READY
        self.command = Command.NOP
        
        #pcr flag
        self.running = False
        self.readyToRun = True
        self.finishPCR = False
        self.protocolEnd = False #JAVA 에서 RUN_REFRIGERATOR 관련된 flag 변수 같음
        self.completed = False
        self.deviceCheck = False

        # task write parameter
        self.protocol_ind = 0
        self.taskEnded = False

        # rx buffer 
        self.rx_action = RxAction()

        # pcr parameters 
        self.preheat = 104
        self.current_list_number = 0
        
        # self.pause_temp = -4 # target pause temperature
        # self.pause_time = 10 # target pause remain time

    def timer_start(self):
        """
            타이머 시작하는 함수.
        """
        self.timer = PCR_Timer(PCR_Task.instance())
        
        #Display serial number
        self.mainUI.gbox_serialNumber.text(self.timer.hid.serial)

        #QTimer start
        self.timer.start()

    def pcr_start(self):
        """
            MainUI 에서 Start 버튼 동작시 실행되는 함수
        """
        self.running = True
        self.complete_PCR = False
        
        self.mainUI.btn_start.setEnabled(False)
        self.mainUI.btn_stop.setEnabled(True)
        self.mainUI.btn_protocol.setEnabled(False)
    
    def pcr_stop(self):
        """
            MainUI 에서 Stop 버튼 동작시 실행되는 함수
            비동기 처리
        """

        if self.state == State.RUN:
            self.timer.stop()

            while True:
                self.timer.hid.write(self.timer.tx_action.tx_stop())

                time.sleep(0.02)

                self.timer.read_buffer()

                time.sleep(0.1)

                if self.state == State.READY:
                    break
            
            self.running = False
            self.taskEnded = False
            self.finishPCR = True
            self.completed = False
            self.readyToRun = True
            self.pcr_end()

            self.timer.start()

    def load_protocol(self, protocol_name):

        try:
            self.protocol = Protocol.load_protocol(protocol_name)
            Protocol.saveRecentProtocolName(protocol_name)
            self.mainUI.table_protocol.display_protocol(self.protocol)
        except ValueError as err:
            QMessageBox.about(self.mainUI, "Invalid_protocol", "올바르지 않은 프로토콜 입니다.")


    def calc_temp(self):
        chamber_temp = self.rx_action['Chamber_TempH'] + self.rx_action['Chamber_TempL'] * 0.1
        heater_temp = self.rx_action['Cover_TempH'] + self.rx_action['Cover_TempL'] * 0.1

        self.mainUI.temp(chamber_temp, heater_temp)
    
    def line_task(self):
        if self.state == State.RUN:
            loop, act_num, left_time = self.rx_action["Current_Loop"], self.rx_action["Current_Action"], self.rx_action["Sec_TimeLeft"]

            for ind, act in enumerate(self.protocol):
                if act['Label'] == 'GOTO':
                    self.mainUI.table_protocol.display_remain(ind, loop if loop != 255 else act['Time'])
                elif act_num == int(act['Label']):
                    self.mainUI.table_protocol.display_remain(ind, -1 if left_time == 0 else left_time)
                else:
                    self.mainUI.table_protocol.display_remain(ind, -1)
                


    def get_device_protocol(self):
        if not self.deviceCheck:
            self.deviceCheck = True
            
            protocol_name = Protocol.loadRecentProtocolName()
            
            if protocol_name:
                try:
                    self.protocol = Protocol.load_protocol(protocol_name)
                    self.mainUI.table_protocol.display_protocol(self.protocol)
                except FileNotFoundError as err:
                    QMessageBox.about(self.mainUI, "protocol_not_found", "최근 프로토콜 파일 존재하지 않음!")
            else:
                pass

                
    def error_check(self):
        pass

    def calc_temp(self):
        """
            Chamber와 LID heater 온도 계산 후 MainUI에 Display 해주는 함수
        """
        chamber_temp = self.rx_action['Chamber_TempH'] + self.rx_action['Chamber_TempL'] * 0.1
        heater_temp = self.rx_action['Cover_TempH'] + self.rx_action['Cover_TempL'] * 0.1

        self.mainUI.temp(chamber_temp, heater_temp)

    def check_action(self):
        """
            self.check_status() 에서
            TASK_WRITE 로 프로토콜 라인을 보낸 후
            rx_buffer 를 check 하는 함수
        """
        action = self.protocol[self.protocol_ind].copy()
        action['Label'] = 250 if action['Label'] == "GOTO" else action['Label']
        
        return action.items() <= self.rx_action.rx_state.items()


    def check_status(self):
        """
            읽어온 rx_buffer의 Status를 기반으로 flag들을 변경해 주는 함수
        """
        if self.state == State.READY:
            if self.rx_action['Current_Operation'] == State_Oper.INIT:
                if self.running and self.taskEnded:
                    if self.readyToRun:
                        self.readyToRun = False
            
            elif self.rx_action['Current_Operation'] == State_Oper.COMPLETE:
                if self.running and self.taskEnded:
                    if self.readyToRun:
                        self.readyToRun = False
                    else:
                        if self.command == Command.NOP:
                            self.running = False
                            self.taskEnded = False
                            self.finishPCR = True
                            self.completed = True
                            self.readyToRun = True
                            self.pcr_end()
            
            elif self.rx_action['Current_Operation'] == State_Oper.INCOMPLETE:
                if self.running and self.taskEnded:
                    if self.readyToRun:
                        self.readyToRun = False
        
        elif self.state == State.TASK_WRITE:
            if self.check_action() and not self.taskEnded:
                #Successfully send protocol line
                if self.protocol_ind == (len(self.protocol) - 1):
                    self.protocol_ind = 0
                    self.taskEnded = True
                else:
                    """
                    210803 YSH :
                        TASK_WRITE 마지막 라인을 정상적으로 보낸 상태에서 protocol_ind = 0 으로 설정했음에도 불구하고,
                        이전의 rx_bufer{State : TASK_WRITE, ~}를 읽어오며 self.protocol_ind += 1을 하여
                        다음 protocol 전송시 첫번째 protocol 라인이 누락되는 현상 발생

                        해결책
                        (*현재*)1. if not self.taskEnded :  후에 self.protocol_ind += 1 수행
                        2. 기존의 self.protocol_ind = 0 을 제거한 후 start 버튼 이벤트에 추가
                    """
                    self.protocol_ind += 1
        
        elif self.state == State.RUN:
            self.running = True
            self.taskEnded = True
            self.readyToRun = False
            pass

    def calc_time(self):
        if self.rx_action['State'] ==  State.RUN:
            self.mainUI.btn_start.setEnabled(False)
            self.mainUI.btn_stop.setEnabled(True)
            self.mainUI.btn_protocol.setEnabled(False)
        
        elif self.rx_action['State'] ==  State.READY:
            self.mainUI.btn_start.setEnabled(True)
            self.mainUI.btn_stop.setEnabled(False)
            self.mainUI.btn_protocol.setEnabled(True)

    
    def set_command(self):
        if self.running:
            if self.taskEnded:
                if self.readyToRun:
                    self.command = Command.TASK_END

                else:
                    if self.state == State.RUN:
                        self.command = Command.NOP
                    
                    else:
                        self.command = Command.GO
            else:
                self.command = Command.TASK_WRITE

        else:
            self.command = Command.NOP

    def pcr_end(self):
        if self.finishPCR:
            if self.completed:
                QMessageBox.about(self.mainUI, "PCR_COMPLITE", "PCR_COMPLITE!")
            else:
                QMessageBox.about(self.mainUI, "PCR_FAIL", "PCR_FAIL!")

            self.finishPCR = False
            self.completed = False

            for ind, act in enumerate(self.protocol):
                self.mainUI.table_protocol.display_remain(ind, -1)
    