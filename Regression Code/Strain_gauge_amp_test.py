import math
import time

import can,time
from can.interfaces.pcan import pcan

import cantools.database 
from CANBase import CANInterface

import cantools
import os


dbc_directory = os.path.join(os.getcwd(), 'Strain Gauge DBC.dbc')
dbc_file = dbc_directory #'..\DBC Tools\output.dbc'
db = cantools.database.load_file(dbc_file)

message = db.get_message_by_name('SGAMP1_data1000Hz')

data = message.encode({
        'SGAMP1_outputVoltage': 100,
        'SGAMP1_ambientTemp': 0,
    })

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
    message = can.Message(arbitration_id=0x3F0, is_extended_id=False,
                          data=data)
    bus.send(message, timeout=0.2)
    # Receive messages
    timeout = time.time() + 5
    while time.time() < timeout:
        msg = bus.recv(timeout=1.0)
        if msg is not None:
            print(f"{msg.arbitration_id:X}: {msg.data}")

