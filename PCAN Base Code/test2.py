
#this works
import can,time
from can.interfaces.pcan import pcan
# Force uninitialize the channel first
try:
    pcan.PCANBasic().Uninitialize(pcan.PCAN_USBBUS2)
except:
    pass  # Ignore if it wasn't initialized
# Now create your bus
with can.Bus(interface='pcan',
              channel='PCAN_USBBUS2',
              bitrate=1000000,
              receive_own_messages=False) as bus:
    # Your code here
    message = can.Message(arbitration_id=0x123, is_extended_id=False,
                          data=[0x11, 0x22, 0x33])
    bus.send(message, timeout=0.2)
    # Receive messages
    timeout = time.time() + 5
    while time.time() < timeout:
        msg = bus.recv(timeout=1.0)
        if msg is not None:
            print(f"{msg.arbitration_id:X}: {msg.data}")





