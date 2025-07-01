import sys
import os
import time
import random
import threading
import ctypes
from ctypes import wintypes
from PySide6 import QtWidgets, QtCore, QtGui

# === Helper for PyInstaller resource access ===
def resource_path(rel_path):
    """
    Get absolute path to resource, works for dev and PyInstaller --onefile.
    """
    base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, rel_path)

# === Win32 SendInput setup ===
INPUT_MOUSE      = 0
MOUSEEVENTF_MOVE = 0x0001

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          wintypes.LONG),
        ("dy",          wintypes.LONG),
        ("mouseData",   wintypes.DWORD),
        ("dwFlags",     wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    class _I(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("_i",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_i",   _I),
    ]

_send_input = ctypes.windll.user32.SendInput
_input_size  = ctypes.sizeof(INPUT)

def send_mouse_move(dx: int, dy: int):
    """
    Simulate a small relative mouse move via SendInput.
    """
    inp = INPUT(type=INPUT_MOUSE,
                mi=MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None))
    _send_input(1, ctypes.byref(inp), _input_size)

# === Worker thread ===
class MoverThread(QtCore.QThread):
    update_status = QtCore.Signal(str)

    def __init__(self, duration_min, interval_s, mickey):
        super().__init__()
        self.duration = duration_min * 60
        self.interval = interval_s
        self.mickey   = mickey
        self._stopped = False

    def run(self):
        end_ts = time.time() + self.duration
        direction = 1
        while time.time() < end_ts and not self._stopped:
            send_mouse_move(direction * self.mickey, 0)
            direction *= -1
            rem = max(0, end_ts - time.time()) / 60
            self.update_status.emit(f"{rem:.1f} min left")
            slept = 0.0
            while slept < self.interval and not self._stopped:
                time.sleep(0.1)
                slept += 0.1
        self.update_status.emit("Stopped" if self._stopped else "Completed")

    def stop(self):
        self._stopped = True

# === Main Window ===
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mickey Bumper")
        self.setMinimumWidth(300)
        self.setMinimumHeight(160)

        # Load and set window & taskbar icon from single multi-size ICO
        icon = QtGui.QIcon(resource_path("icon256x256.ico"))
        self.setWindowIcon(icon)

        form = QtWidgets.QFormLayout(self)
        self.dur = QtWidgets.QLineEdit("60")
        form.addRow("Duration (min):", self.dur)
        self.ivl = QtWidgets.QLineEdit("10")
        form.addRow("Interval (sec):", self.ivl)
        self.mic = QtWidgets.QLineEdit("1")
        form.addRow("Mickeys (pixels):", self.mic)

        self.status = QtWidgets.QLabel("Idle")
        form.addRow("Status:", self.status)

        h = QtWidgets.QHBoxLayout()
        self.btn_start = QtWidgets.QPushButton("Start")
        h.addWidget(self.btn_start)
        self.btn_stop  = QtWidgets.QPushButton("Stop")
        h.addWidget(self.btn_stop)
        form.addRow(h)

        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.thread = None

    def start(self):
        try:
            d = float(self.dur.text())
            i = float(self.ivl.text())
            m = int(self.mic.text())
            if i < 5.0:
                i = 5.0
                self.ivl.setText("5")
            if d <= 0 or m == 0:
                raise ValueError
        except ValueError:
            self.status.setText("Enter valid positive numbers.")
            return

        self.thread = MoverThread(d, i, m)
        self.thread.update_status.connect(self.status.setText)
        self.thread.start()
        self.btn_start.setEnabled(False)

    def stop(self):
        if self.thread:
            self.thread.stop()
            self.thread.wait()
        self.btn_start.setEnabled(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
