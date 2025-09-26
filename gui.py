from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QComboBox, QVBoxLayout, QWidget, QGroupBox,
    QHBoxLayout, QDateTimeEdit, QGridLayout
)
from PyQt6.QtCore import QDateTime
import sys
import serial.tools.list_ports
from telemetry import TelemetryService
from command_handler import CommandHandler

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

        #################################################################################
        ### Create group box 1 ###
        self.group_box1 = QGroupBox("Available USB Serial Ports")
        layout1 = QVBoxLayout()

        # Create dropdown
        self.combo = QComboBox()
        self.combo.addItems(usb_serial_ports)
        layout1.addWidget(self.combo)

        # Create connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_device)
        layout1.addWidget(self.connect_button)

        # Create disconnect button
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_from_device)
        layout1.addWidget(self.disconnect_button)


        self.group_box1.setLayout(layout1)
        
        #################################################################################
        ### Create group box 2 ###
        self.group_box2 = QGroupBox("Data")
        layout2 = QGridLayout()
        self.group_box2.setLayout(layout2)

        # Temperature label
        self.temperature_label = QPushButton("Temperature: N/A")
        layout2.addWidget(self.temperature_label, 0, 0)

        # Request temperature button
        self.request_temp_button = QPushButton("Request Temperature")
        self.request_temp_button.clicked.connect(self.request_temperature)
        layout2.addWidget(self.request_temp_button, 0, 1)

        # Date time label
        self.date_time_label = QPushButton("Date/Time: N/A")
        layout2.addWidget(self.date_time_label, 1, 0)

        # Request date time button
        self.request_date_time_button = QPushButton("Request Date/Time")
        self.request_date_time_button.clicked.connect(self.get_date_time)
        layout2.addWidget(self.request_date_time_button, 1, 1)
    
        # Sync time button
        self.sync_time_button = QPushButton("Sync PC Time to Device")
        self.sync_time_button.clicked.connect(self.sync_time_to_device)
        layout2.addWidget(self.sync_time_button, 2, 0)

        # Delete log button (not implemented)
        self.start_new_log_button = QPushButton("Delete Log")
        self.start_new_log_button.clicked.connect(self.start_new_log)
        layout2.addWidget(self.start_new_log_button, 3, 0)



        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.group_box1)
        main_layout.addWidget(self.group_box2)

        
        # Wrap layout in a QWidget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set central widget
        self.setCentralWidget(central_widget)

        self.show()


    def connect_to_device(self):
        selected_port = self.combo.currentText()
        if selected_port:
            print(f"Connecting to {selected_port}...")
            self.telemetry_service = TelemetryService(selected_port)
            self.handler = CommandHandler(self.telemetry_service)
        else:
            print("No port selected.")

    def disconnect_from_device(self):
        if hasattr(self, 'telemetry_service'):
            print("Disconnecting...")
            temp = self.telemetry_service.stop()
        else:
            print("No device connected.")

    def request_temperature(self):
        if hasattr(self, 'handler'):
            print("Requesting temperature...")
            temp = self.handler.get_temp()
            print(f"Temperature: {temp} °C")
            self.temperature_label.setText(f"Temperature: {temp} °C")
        else:
            print("No device connected.")

    def get_date_time(self):
        if hasattr(self, 'handler'):
            print("Requesting date/time...")
            date = self.handler.get_time()
            print(f"Date/Time: {date}")
            # Date/time will be printed in the command handler's process method
            self.date_time_label.setText(f"Date/Time: {date}")
        else:
            print("No device connected.")

    def sync_time_to_device(self):
        if hasattr(self, 'handler'):
            print("Syncing PC time to device...")
            self.handler.set_time()
        else:
            print("No device connected.")

    def start_new_log(self):
        print("Start new log.")
        if hasattr(self, 'handler'):
            self.handler.start_new_log()
        else:
            print("No device connected.")




app = QApplication(sys.argv)
w = MainWindow()
app.exec()