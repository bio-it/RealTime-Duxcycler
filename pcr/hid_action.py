from pcr.constant import Command
from ctypes import *

class TxAction:
    AF_GOTO				= 250
    TX_BUFSIZE          = 65

    TX_CMD              = 1;    TX_ACTNO            = 2
    TX_TEMP			    = 3;    TX_TIMEH			= 4
    TX_TIMEL			= 5;    TX_LIDTEMP			= 6
    TX_REQLINE			= 7;    TX_CURRENT_ACT_NO 	= 8
    TX_BOOTLOADER		= 10

    def __init__(self):
        self.tx_Buffer = create_string_buffer(TxAction.TX_BUFSIZE)
        self.tx_clear()

    def tx_clear(self):
        memset(self.tx_Buffer, 0, TxAction.TX_BUFSIZE)

    def tx_NOP(self):
        self.tx_clear()
        return self.tx_Buffer

    def tx_taskWrite(self, action, preheat, current_act_no):
        self.tx_clear()
        
        nlabel = TxAction.AF_GOTO if action['Label'] == 'GOTO' else int(action['Label'])
        ntemp = int(action['Temp'])
        ntime = int(action['Time'])
        # nlabel, ntemp, ntime = map(lambda x : TxAction.AF_GOTO if x == 'GOTO' else int, action)
        npreheat = int(preheat)
        #print('nlabel : {}, ntemp : {}, ntime : {}'.format(nlabel, ntemp, ntime))

        self.tx_Buffer[TxAction.TX_CMD] = Command.TASK_WRITE
        self.tx_Buffer[TxAction.TX_ACTNO] = nlabel
        self.tx_Buffer[TxAction.TX_TEMP] = ntemp
        self.tx_Buffer[TxAction.TX_TIMEH] = ntime >> 8
        self.tx_Buffer[TxAction.TX_TIMEL] = ntime & 0xFF
        self.tx_Buffer[TxAction.TX_LIDTEMP] = npreheat
        self.tx_Buffer[TxAction.TX_CURRENT_ACT_NO] = current_act_no
        self.tx_Buffer[TxAction.TX_REQLINE] = current_act_no
        #print('lib : ', self.tx_Buffer[TxAction.TX_ACTNO], self.tx_Buffer[TxAction.TX_LIDTEMP], self.tx_Buffer[TxAction.TX_CURRENT_ACT_NO])

        return self.tx_Buffer

    def tx_taskEnd(self):
        self.tx_clear()
        self.tx_Buffer[TxAction.TX_CMD] = Command.TASK_END
        return self.tx_Buffer

    def tx_go(self):
        self.tx_clear()
        self.tx_Buffer[TxAction.TX_CMD] = Command.GO
        return self.tx_Buffer

    def tx_stop(self):
        self.tx_clear()
        self.tx_Buffer[TxAction.TX_CMD] = Command.STOP
        return self.tx_Buffer

    def tx_bootLoader(self):
        self.tx_clear()
        self.tx_Buffer[TxAction.TX_CMD] = Command.BOOTLOADER
        return self.tx_Buffer

    def tx_requestLine(self, reqline):
        self.tx_clear()
        self.tx_Buffer[TxAction.TX_REQLINE] = reqline
        return self.tx_Buffer

class RxAction:
    AF_GOTO			=	250
    RX_BUFSIZE		=	64

    RX_STATE 		= 	0;     RX_RES			=	1
    RX_CURRENTACTNO	=	2;     RX_CURRENTLOOP	=	3
    RX_TOTALACTNO	=	4;     RX_KP			=	5
    RX_KI			=	6;     RX_KD			=	7
    RX_LEFTTIMEH	=	8;     RX_LEFTTIMEL	    =	9
    RX_LEFTSECTIMEH	=	10;    RX_LEFTSECTIMEL	=	11
    RX_LIDTEMPL		=	13;    RX_LIDTEMPH		=	12
    RX_CHMTEMPH		=	14;    RX_CHMTEMPL		=	15
    RX_PWMH			=	16;    RX_PWMDIR		=	18
    RX_PWML			=	17;    RX_LABEL		    =	19
    RX_TEMP			=	20;    RX_TIMEH		    =	21
    RX_TIMEL		=	22;    RX_LIDTEMP		=	23
    RX_REQLINE		=	24;    RX_ERROR		    =	25
    RX_CUR_OPR		=	26;    RX_SINKTEMPH	    =	27
    RX_SINKTEMPL	=	28;    RX_KP_1			=	39
    RX_KI_1			=	33;    RX_KD_1			=	37
    RX_SERIALH		=	41 #not using this version.
    RX_SERIALL		=	42 #only bluetooth version
    RX_SERIALRESERV	=	43;    RX_VERSION		=	44
    
    def __init__(self):
        self.isReceiveOnce = False
        self.rx_state = {'State' : 0, 'Res' : 0,
                         'Cover_TempH' : 0, 'Cover_TempL' : 0,
                         'Chamber_TempH' : 0, 'Chamber_TempL' : 0,
                         'Heatsink_TempH' : 0, 'Heatsink_TempL' : 0,
                         'Current_Operation' : 0, 'Current_Action' : 0,
                         'Current_Loop' : 0, 'Total_Action' : 0,
                         'Error' : 0, 'Serial_H' : 0, 'Serial_L' : 0,
                         'Total_TimeLeft' : 0, 'Sec_TimeLeft' : 0,
                         'Firmware_Version' : 0,
                         'Label' : 0, 'Temp' : 0, 'Time_H' : 0, 'Time_L' : 0,
                         'ReqLine' : 0}
        
    def set_info(self, buffer):
        buffer = list(buffer) #210703 HUN modified

        self.rx_state['State']              = buffer[RxAction.RX_STATE]
        self.rx_state['Res']                = buffer[RxAction.RX_RES]
        self.rx_state['Current_Action']     = buffer[RxAction.RX_CURRENTACTNO]
        self.rx_state['Current_Loop']       = buffer[RxAction.RX_CURRENTLOOP]
        self.rx_state['Total_Action']       = buffer[RxAction.RX_TOTALACTNO]
        self.rx_state['Total_TimeLeft']     = (buffer[RxAction.RX_LEFTTIMEH] << 8) + buffer[RxAction.RX_LEFTTIMEL]
        self.rx_state['Sec_TimeLeft']       = float((buffer[RxAction.RX_LEFTSECTIMEH] << 8) + buffer[RxAction.RX_LEFTSECTIMEL])
        self.rx_state['Cover_TempH']        = buffer[RxAction.RX_LIDTEMPH]
        self.rx_state['Cover_TempL']        = buffer[RxAction.RX_LIDTEMPL]
        self.rx_state['Chamber_TempH']      = buffer[RxAction.RX_CHMTEMPH]
        self.rx_state['Chamber_TempL']      = buffer[RxAction.RX_CHMTEMPL]
        self.rx_state['Heatsink_TempH']     = buffer[RxAction.RX_SINKTEMPH]
        self.rx_state['Heatsink_TempL']     = buffer[RxAction.RX_SINKTEMPL]
        self.rx_state['Current_Operation']  = buffer[RxAction.RX_CUR_OPR]
        self.rx_state['Error']              = buffer[RxAction.RX_ERROR]
        self.rx_state['Serial_H']           = buffer[RxAction.RX_SERIALH]
        self.rx_state['Serial_L']           = buffer[RxAction.RX_SERIALL]
        self.rx_state['Firmware_Version']   = buffer[RxAction.RX_VERSION]
        self.rx_state['Label']              = buffer[RxAction.RX_LABEL]
        self.rx_state['Temp']               = buffer[RxAction.RX_TEMP]
        self.rx_state['Time_H']             = buffer[RxAction.RX_TIMEH]
        self.rx_state['Time_L']             = buffer[RxAction.RX_TIMEL]
        self.rx_state['ReqLine']            = buffer[RxAction.RX_REQLINE]
        self.rx_state["Time"]               = (self.rx_state['Time_H'] << 8) + self.rx_state['Time_L']
        self.isReceiveOnce = True
    
    def __getitem__(self, key):
        return self.rx_state[key]
 
    def isValidBuffer(self):
        return self.isReceiveOnce    
