import serial

# Open serial port
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Transmit binary data
temp_request = b'\x7E\x7E\x06\x00\x00\x00'
ser.write(temp_request)

# Receive binary data
rx_buffer = b''
while True:
    byte = ser.read(1)
    if not byte:
        break  # Timeout, no more data
    rx_buffer += byte
    if byte == b'\n':  # Example: stop at newline
        break
print("Received:", rx_buffer)

ser.close()