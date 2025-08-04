import serial
import threading
import queue

SYNC_BYTE = 0x7E

class TelemetryMsg:
    def __init__(self):
        self.cmd = 0
        self.len = 0
        self.data = bytearray()

class TelemetryService:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.msg_queue = queue.Queue()
        self.message_callback = None
        self.running = True
        self.thread = threading.Thread(target=self.service_loop)
        self.thread.start()

    def set_message_callback(self, cb):
        self.message_callback = cb

    def feed_byte(self, rx_byte):
        # State machine variables
        if not hasattr(self, 'state'):
            self.state = 0
            self.rxMsg = TelemetryMsg()
            self.dataIndex = 0
            self.dataLen = 0

        if self.state == 0:  # eSYNC_1
            if rx_byte == SYNC_BYTE:
                self.state = 1
        elif self.state == 1:  # eSYNC_2
            if rx_byte == SYNC_BYTE:
                self.state = 2
            else:
                self.state = 0
        elif self.state == 2:  # eCMD
            self.rxMsg.cmd = rx_byte
            self.state = 3
        elif self.state == 3:  # eDATA_LEN
            self.rxMsg.len = rx_byte
            self.dataLen = rx_byte
            self.dataIndex = 0
            if rx_byte == 0:
                self.state = 5
            else:
                self.rxMsg.data = bytearray()
                self.state = 4
        elif self.state == 4:  # eDATA
            self.rxMsg.data.append(rx_byte)
            self.dataIndex += 1
            if self.dataIndex >= self.dataLen:
                self.state = 5
        elif self.state == 5:  # eCRC_1
            self.state = 6
        elif self.state == 6:  # eCRC_2
            self.state = 0
            # CRC check can be added here
            if self.message_callback:
                self.message_callback(self.rxMsg)

    def service_loop(self):
        while self.running:
            if self.ser.in_waiting:
                rx_byte = self.ser.read(1)
                if rx_byte:
                    self.feed_byte(rx_byte[0])

    def stop(self):
        self.running = False
        self.thread.join()
        self.ser.close()

    def telemetry_service_response(self, msg):
        # Build the response buffer
        tx_buff = bytearray()
        tx_buff.append(SYNC_BYTE)  # Start byte
        tx_buff.append(SYNC_BYTE)  # Second sync byte
        tx_buff.append(msg.cmd)    # Command
        tx_buff.append(msg.len)    # Length
        if msg.len > 0:
            tx_buff.extend(msg.data)  # Data
        tx_buff.append(0)  # CRC placeholder
        tx_buff.append(0)  # CRC placeholder
        # Send the buffer over serial
        self.ser.write(tx_buff)

# Example usage:
def my_callback(msg):
    print(f"Received: cmd={msg.cmd}, len={msg.len}, data={msg.data}")

# To stop the service:
# service.stop()