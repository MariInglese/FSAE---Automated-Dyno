#import libraries 
import csv 
import os 
import time

import cantools.database

#import CANInterface class
from CANBase import CANInterface 

# File path to data log that we are going to replay 
file_path = r'Software\playgroud\trace_replay_logs\replay_log_2.1.csv'

#open and read csv file (data log)
with open(file_path, mode='r', newline='') as csvfile: 
    reader = csv.reader(csvfile)

    #import message data class
    from data.message_data import MessageData

    #load the dbc files - why do we need hfi dbc?
    hfi_dbc = os.path.join(os.getcwd(), r'Software\DBC Tools\HardwareInjector.dbc')
    hfi_db = cantools.database.load_file(hfi_dbc)

    vcu_torque_dbc = os.path.join(os.getcwd(), r'Software\DBC Tools\M150_VCU_TORQUE.dbc')
    vcu_torque_db = cantools.database.load_file(vcu_torque_dbc)

    mc_torque_dbc = os.path.join(os.getcwd(), r'Software\DBC Tools\mc_test.dbc')
    mc_torque_db = cantools.database.load_file(mc_torque_dbc)

    time.sleep(2)

    



