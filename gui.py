from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QComboBox, QVBoxLayout, QWidget
import sys
import serial.tools.list_ports

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temperature Logger")

        # Find available USB serial ports
        ports = serial.tools.list_ports.comports()
        usb_serial_ports = [
            port.device for port in ports
            if 'USB' in port.description or 'usb' in port.description or 'Serial' in port.description
        ]

        # Create dropdown
        self.combo = QComboBox()
        self.combo.addItems(usb_serial_ports)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.combo)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.show()


app = QApplication(sys.argv)
w = MainWindow()
app.exec()