import sys
import ui.main_ui as ui
import pcr.timer as PCR_timer
from pcr.task import PCR_Task
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    pcr_task = PCR_Task.instance(ui.window)
    pcr_task.timer_start()
    sys.exit(ui.app.exec())