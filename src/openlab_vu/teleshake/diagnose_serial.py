"""Probe a serial port at multiple baud rates to find a responding Teleshake 1536."""
import serial

# GetInfo command (0x23) to address 0: ctrl=0x60, cmd=0x23, data=0x00*3, crc=0x83
FRAME = bytes([0x60, 0x23, 0x00, 0x00, 0x00, 0x83])
PORT = "COM1"

for baud in [9600, 19200, 38400, 57600, 115200, 4800, 2400]:
    try:
        s = serial.Serial(PORT, baudrate=baud, timeout=2)
        s.read_all()
        s.write(FRAME)
        s.flush()
        reply = s.read(6)
        s.close()
        if reply:
            print(f"REPLY at {baud}: {reply.hex()}")
        else:
            print(f"{baud}: no reply")
    except Exception as e:
        print(f"{baud}: error - {e}")
