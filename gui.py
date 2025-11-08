from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QComboBox, QVBoxLayout, QWidget, QGroupBox,
    QHBoxLayout, QDateTimeEdit, QGridLayout, QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)
from PyQt6.QtCore import QDateTime, QTimer
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
        self.group_box2 = QGroupBox("Configuration")
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

        # Create dropdown for tiem interval
        self.time_interval_combo = QComboBox()
        self.time_interval_combo.addItems(["1 min", "5 min", "10 min", "30 min", "60 min"])
        layout2.addWidget(self.time_interval_combo,4 ,0)

        # Configure time interval button
        self.time_interval_button = QPushButton("Configure time interval")
        self.time_interval_button.clicked.connect(self.configure_time_interval)
        layout2.addWidget(self.time_interval_button, 4, 1)

        #################################################################################
        ### Create group box 3 ###
        self.group_box3 = QGroupBox("Data")
        layout3 = QGridLayout()
        self.group_box3.setLayout(layout3)

        # Log data list table
        self.table = QTableWidget(0, 0)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Temperature (°C)"])
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Temperature (°C)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout3.addWidget(self.table)

        # Request log data button
        self.request_log_data_button = QPushButton("Request log data")
        self.request_log_data_button.clicked.connect(self.request_log_data)
        layout3.addWidget(self.request_log_data_button, 1, 0)

        self.export_button = QPushButton("Export CSV")
        self.export_button.clicked.connect(self.export_table_csv)
        layout3.addWidget(self.export_button, 1, 2)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.group_box1)
        main_layout.addWidget(self.group_box2)
        main_layout.addWidget(self.group_box3)

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
            # pass callback into the handler so it can notify the GUI
            self.handler = CommandHandler(self.telemetry_service, callback=self.callback)
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

    def configure_time_interval(self):
        if hasattr(self, 'handler'):
            interval_text = self.time_interval_combo.currentText()
            interval_minutes = int(interval_text.split()[0])
            print(f"Configuring time interval to {interval_minutes} minutes...")
            self.handler.set_log_interval(interval_minutes)
        else:
            print("No device connected.")

    def request_log_data(self):
        if hasattr(self, 'handler'):
            print("Requesting log data...")
            log_data = self.handler.stream_logs()
            self.table.setRowCount(0)  # Clear existing data
        else:
            print("No device connected.")

    def callback(self, event, payload):
        if event == "temperature":
            temp = payload
            self.temperature_label.setText(f"Temperature: {temp:.2f} °C")
        elif event == "date_time":
            ts = payload
            self.date_time_label.setText(f"Date/Time: {ts}")
        elif event == "log":
            log_entry = payload
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            timestamp = f"{log_entry[0]+2000:04}-{log_entry[1]:02}-{log_entry[2]:02} {log_entry[3]:02}:{log_entry[4]:02}:{log_entry[5]:02}"
            temperature = log_entry[7]
            timestamp_item = QTableWidgetItem(timestamp)
            temperature_item = QTableWidgetItem(f"{temperature:.2f}")
            self.table.setItem(row_position, 0, timestamp_item)
            self.table.setItem(row_position, 1, temperature_item)

    def export_table_csv(self):
        """Open Save dialog and write CSV file."""
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        import csv
        cols = self.table.columnCount()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = [self.table.horizontalHeaderItem(c).text() if self.table.horizontalHeaderItem(c) else "" for c in range(cols)]
            writer.writerow(headers)
            for r in range(self.table.rowCount()):
                row = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(cols)]
                writer.writerow(row)

app = QApplication(sys.argv)
w = MainWindow()
app.exec()