# Importing libraries 
import csv, os, time, math, can, cantools
import cantools.database 
from CANBase import CANInterface
from message_data import MessageData
from can.interfaces.pcan import pcan

file_path = r'fake_csv.csv'

#open and read csv file

from message_data import MessageData

dbc_directory = os.path.join(os.getcwd(), r'hv500_can2_map_v25_SID.dbc')
dbc_file = dbc_directory
db = cantools.database.load_file(dbc_file)

message = db.get_message_by_name('HV500_SetAcCurrent')

with can.Bus(interface='pcan',
            channel='PCAN_USBBUS1',
            bitrate=1000000,
            receive_own_messages=False) as bus:

    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Iterate through CSV
        for row in reader: 
            torque = float(row[1])              # Fetch torque feedback
            print(torque)
            data = message.encode({'CMD_TargetAcCurrent': torque})  # Encode message
            tx_message = can.Message(arbitration_id=0x036, is_extended_id=False,
                        data=data)                # Formulate message
            bus.send(tx_message, timeout=0.2)      # Send message to BUS BUS BUS
            if tx_message is not None:
                print(f"{tx_message.arbitration_id:X}: {tx_message.data}")
                
            time.sleep(1)                       # Wait for 1s before updating