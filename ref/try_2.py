import serial
import time

ser = serial.Serial()
ser.baudrate = 9600
ser.port = "COM9"
# parity=serial.PARITY_NONE,
parity=serial.PARITY_EVEN,
stopbits=serial.STOPBITS_ONE,
# bytesize=serial.EIGHTBITS
bytesize=serial.SEVENBITS
ser.open()

# cw = b'0xaa,0xf4'
# ser.write(serial.to_bytes(cw))
# print(cw)
# time.sleep(1)

# cw = [0xaa,0xf4]
# ser.write(serial.to_bytes(cw))
# print(cw)
# time.sleep(1)


# cw = b'\xaa\xf4'
# ser.write(serial.to_bytes(cw))
# print(cw)

# n = ser.write(b'\xaa\xf4')
# n += ser.write(bytes([2]))
# n += ser.write(bytes([3]))
# print("bytes written ", n)


# while(1):
# byte_read = []
# byte_read = ser.readline()
# print(byte_read)

# byte_read = ser.read().decode("ascii")
# byte_read = ser.read(13).hex()
byte_read = ser.read(23)
# byte_read += ser.read(1)
# print(byte_read.decode("utf-8"))
print(byte_read)
ser.close()