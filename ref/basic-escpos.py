from escpos.printer import Usb
import win32com.client
import usb.core
from usb.backend import libusb1
import libusb_package

""" Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
wmi = win32com.client.GetObject ("winmgmts:")
for usb in wmi.InstancesOf ("Win32_USBHub"):
    print(usb.DeviceID)
backend = libusb1.get_backend(find_library=libusb_package.find_library)
# p = Usb(0x04b8, 0x0e27, 0, profile="TM-T88II")
p = Usb(0x04b8, 0x0e27, 0)
p.text("Hello World\n")
p.image("logo.gif")
p.barcode('4006381333931', 'EAN13', 64, 2, '', '')
p.cut()


# from escpos.printer import Serial

# """ 9600 Baud, 8N1, Flow Control Enabled """
# p = Serial(devfile='/dev/tty.usbserial',
#            baudrate=9600,
#            bytesize=8,
#            parity='N',
#            stopbits=1,
#            timeout=1.00,
#            dsrdtr=True)

# p.text("Hello World\n")
# p.qr("You can readme from your smartphone")
# p.cut()


