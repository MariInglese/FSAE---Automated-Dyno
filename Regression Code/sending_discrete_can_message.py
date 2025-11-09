# Importing libraries 
import csv, os, time, math, can, cantools
import cantools.database 
from CANBase import CANInterface
from message_data import MessageData
from can.interfaces.pcan import pcan


# File path to i2 log 
file_path = r'replay_log_2.1.csv'

        # Dyno conditions and real endurance conditions will have different throttle requests
        # Start with reading throttle request and outputting identical throttle request
        # Second, use dyno load adjustment to back calculate throttle request from output power
        # Power = torque * rpm
        # Adjusted Torque request = Output Power / some different rpm


        # Forget the fault injector
        # Part 0: Create dummmy CSV to validate proper communication 
        #         from laptop to PCAN to vcu

        # Part 1: Read torque command from i2 log file from endurance
        #         Send exact torque command to PCAN to VCU over CAN

        # Part 2: Adjust torque request depending on dyno factor based on output power and rpm


dbc_directory = os.path.join(os.getcwd(), 'Strain Gauge DBC.dbc')
dbc_file = dbc_directory 
db = cantools.database.load_file(dbc_file)

message = db.get_message_by_name('SGAMP1_data1000Hz')

"""
data = message.encode({
    'VCU_INV_Direction_Command': 0,
    'VCU_INV_Inverter_Discharge': 0,
    'VCU_INV_Inverter_Enable': 1,
    'VCU_INV_Speed_Command': 0,
    'VCU_INV_Speed_Mode_Enable': 0,
    'VCU_INV_Torque_Command': 500,
    'VCU_INV_Torque_Limit_Command': 1000,
})
"""
data = message.encode({
    'SGAMP1_ambientTemp': 100,
    'SGAMP1_outputVoltage': -10000,
})

is_running = 1


with can.Bus(interface='pcan',
              channel='PCAN_USBBUS1',
              bitrate=1000000,
              receive_own_messages=False) as bus:
    # Your code here
    message = can.Message(arbitration_id=0x3F0, is_extended_id=False,
                          data=data)

    
    while is_running: 
        bus.send(message, timeout=0.2) 
        if message is not None:
            print(f"{message.arbitration_id:X}: {message.data}")
            
        time.sleep(0.0001)
        
    
