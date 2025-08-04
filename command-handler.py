import time
from telemetry import TelemetryMsg, TelemetryService

class RTC_Time:
    def __init__(self):
        self.tm_year = 0
        self.tm_mon = 0
        self.tm_mday = 0
        self.tm_hour = 0
        self.tm_min = 0
        self.tm_sec = 0

class CommandHandler:
    def __init__(self, telemetry_service):
        self.tm = RTC_Time()
        self.telemetry_service = telemetry_service
        self.telemetry_service.set_message_callback(self.process)

    def get_firmware_version(self):
        msg = TelemetryMsg()
        msg.cmd = 0x01  # eFW_VER
        msg.len = 0
        self.telemetry_service.telemetry_service_response(msg)

    def get_hardware_version(self):
        msg = TelemetryMsg()
        msg.cmd = 0x02  # eHW_VER
        msg.len = 0
        self.telemetry_service.telemetry_service_response(msg)

    def set_time(self):
        now = time.localtime()
        msg = TelemetryMsg()
        msg.cmd = 0x03  # eSET_TIME
        msg.len = 6
        year = now.tm_year - 2000
        msg.data = bytearray([
            year,
            now.tm_mon,
            now.tm_mday,
            now.tm_hour,
            now.tm_min,
            now.tm_sec
        ])
        self.telemetry_service.telemetry_service_response(msg)

    def get_time(self):
        msg = TelemetryMsg()
        msg.cmd = 0x04  # eGET_TIME
        msg.len = 0
        self.telemetry_service.telemetry_service_response(msg)

    def get_temp(self):
        msg = TelemetryMsg()
        msg.cmd = 0x06  # eTEMP
        msg.len = 0
        self.telemetry_service.telemetry_service_response(msg)

    def process(self, msg):
        print(f"Message received: cmd=0x{msg.cmd:02X}, len={msg.len}")
        if msg.cmd == 0x01:  # eFW_VER
            print(f"Firmware Version:{msg.data[0]}.{msg.data[1]}.{msg.data[2]}")
        elif msg.cmd == 0x02:  # eHW_VER
            print(f"Hardware Version:{msg.data[0]}.{msg.data[1]}.{msg.data[2]}")
        elif msg.cmd == 0x03:  # eSET_TIME
            print("Set Time Command")
        elif msg.cmd == 0x04:  # eGET_TIME
            print(f"Get Time Command:{msg.data[0]}.{msg.data[1]}.{msg.data[2]} {msg.data[3]}:{msg.data[4]}:{msg.data[5]}")
        elif msg.cmd == 0x05:  # eCPU_TEMP
            print("CPU Temp Command")
            # Add CPU temp logic if needed
        elif msg.cmd == 0x06:  # eTEMP
            print(f"Temperature Command: {msg.data[0]}")
        elif msg.cmd == 0x07:  # eSET_LOG_INTERVAL
            print("Set Log Interval Command")
        elif msg.cmd == 0x08:  # eGET_LOG_INTERVAL
            print("Get Log Interval Command")
        elif msg.cmd == 0x09:  # eSTREAM_LOGS
            print("Stream Logs Command")
        else:
            print("Unknown Command")

service = TelemetryService('/dev/ttyUSB0')
handler = CommandHandler(service)

handler.get_firmware_version()
handler.get_hardware_version()
handler.set_time()
handler.get_time()
handler.get_temp()
