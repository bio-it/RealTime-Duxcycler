
import sys
import PyQt6
from PyQt6 import QtCore
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QAbstractItemView, QApplication, QFileDialog, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QVBoxLayout, QPushButton, QWidget, QMainWindow, QFrame, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QFileDevice, QRect, Qt
from pcr.protocol import Protocol
from pcr.task import PCR_Task



class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("DuxCycler") # set title
        self.setGeometry(100, 100, 390, 470) # (pos_x, pos_y , width, height)
        
        #Disable window resize
        self.setFixedSize(390, 470)

        self.gbox_serialNumber = GBox_Label("Serial Number", self)
        self.gbox_serialNumber.text("NOT CONNECTED")
        self.gbox_serialNumber.setGeometry(10, 10, 150, 60)

        self.gbox_chamber = GBox_Label("CHAMBER", self)
        self.gbox_chamber.text("")
        self.gbox_chamber.setGeometry(170, 10, 100, 60)

        self.gbox_lidHeater = GBox_Label("LID HEATER", self)
        self.gbox_lidHeater.text("")
        self.gbox_lidHeater.setGeometry(280, 10, 100, 60)

        self.table_protocol = Protocol_Table(self)

        self.btn_start = QPushButton("Start", self)
        self.btn_start.setGeometry(70, 400, 60, 30)

        self.btn_stop = QPushButton("Stop", self)
        self.btn_stop.setGeometry(150, 400, 60, 30)
        self.btn_stop.setEnabled(False)

        self.btn_protocol = QPushButton("Load protocol", self)
        self.btn_protocol.setGeometry(230, 400, 90, 30)
        self.btn_protocol.setEnabled(True)

        #Connect Event
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_protocol.clicked.connect(self.load_protocol)

    def temp(self, chamber_temp, heater_temp):
        self.gbox_chamber.text(str(chamber_temp) + "℃")
        self.gbox_lidHeater.text(str(heater_temp) + "℃")

    def start(self):
        PCR_Task.instance().pcr_start()

    def stop(self):
        PCR_Task.instance().pcr_stop()

    def load_protocol(self):
        filename = QFileDialog.getOpenFileName(self, 'Select Protocol', 'C:\\mPCR\\protocols', filter='*.txt')[0]
        filename = filename.split('/')[-1][:-4]
        PCR_Task.instance().load_protocol(filename)

class GBox_Label(QGroupBox):
    def __init__(self, title, parent=None):
        super(GBox_Label, self).__init__(parent)
        self.setTitle(title)
        
        self.layout = QVBoxLayout()
        self.label = QLabel("")

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def text(self, _str):
        self.label.setText(_str)

class Protocol_Table(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_header = ["No", "Temp", "Time", "Remain"]
        self.header_num = len(self.table_header)
        
        self.table = QTableWidget(self)
        self.table.setGeometry(10, 110, 370, 250)

        #Disable horizontal scroll bar
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #self.table.horizontalScrollBar().setVisible(False)
        
        #Set col num
        self.table.setColumnCount(self.header_num)

        #Set table header
        self.table.setHorizontalHeaderLabels(self.table_header)

        #Resize column width & fix them
        for col_num in range(0, self.header_num):
            self.table.setColumnWidth(col_num, self.table.width()/self.header_num) 
            #self.table.horizontalHeader().setSectionResizeMode(col_num, QHeaderView.ResizeMode.Stretch)#https://stackoverflow.com/questions/18293403/columns-auto-resize-to-size-of-qtableview
            self.table.horizontalHeader().setSectionResizeMode(col_num, QHeaderView.ResizeMode.Fixed)

        #Disable display row number
        self.table.verticalHeader().setVisible(False)
        
        #Disable focus and selection
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        #Disable edit mode
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


    def display_protocol(self, protocol):
        #Set row
        self.table.setRowCount(len(protocol))
        
        #Display loaded protocol
        for r_ind, line in enumerate(protocol):
            for c_ind, el in enumerate(line.values()):
                t_item = QTableWidgetItem(str(el))
                
                #Algin text center
                t_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                #Put them in
                self.table.setItem(r_ind, c_ind, t_item)

    def display_remain(self, ind, time_sec):
        t_item = QTableWidgetItem(str("" if time_sec==-1 else int(time_sec)))
        t_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(ind, 3, t_item)
        


app = QApplication(sys.argv)
app.setStyle('Fusion') #windowsvista Windows Fusion
window = MainUI()
window.show()