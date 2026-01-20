# Importing libraries 
import csv, os, time, math, can, cantools
import cantools.database 
from can.interfaces.pcan import pcan

# First column time
# Second column torque
file_path = r'ramp_up.csv'
#write_file = w

numMissing = 0
toggle = 0 

#open and read csv file
dbc_directory = os.path.join(os.getcwd(), r"C:\\GitHub\\FSAE---Automated-Dyno\DBC Tools\\20230411_Gen5_CAN_DBC_PantherRacing_2024_01_15.dbc")
dbc_file = dbc_directory
db = cantools.database.load_file(dbc_file)

message = db.get_message_by_name('M192_Command_Message')

with can.Bus(interface='pcan',
            channel='PCAN_USBBUS1',
            bitrate=1000000,
            receive_own_messages=False) as bus:

    with open(file_path, mode='r', newline='') as csvfile:
        reader1 = csv.reader(csvfile)
        # Get time in between samples 
        first_row = next(reader1)
        print(first_row)
        second_row = next(reader1) 
        print(second_row)
        sample_time  = float(second_row[0]) - float(first_row[0]) # 0 is time, 1 is torque
        #print(sample_time)
    with open(file_path, mode='r', newline='') as csvfile:
        reader2 = csv.reader(csvfile)
        # Iterate through CSV
        counter = 5
        for row in reader2: 
            try: 
                numMissing = numMissing + 1
                torque = float(row[1])              # Fetch torque feedback
                #print(torque)
                
                data = message.encode({'VCU_INV_Torque_Command': torque,'VCU_INV_Speed_Command': 0.0,'VCU_INV_Direction_Command': 1,'VCU_INV_Inverter_Enable': 1,'VCU_INV_Inverter_Discharge': 1,'VCU_INV_Speed_Mode_Enable': 0,'VCU_INV_Torque_Limit_Command': 100.0},strict=False)  # Encode message
                
                tx_message = can.Message(arbitration_id=0xC0, is_extended_id=False,
                            data=data)                # Formulate message
                bus.send(tx_message, timeout=0.2)      # Send message to BUS BUS BUS
                if tx_message is not None:
                    pass
                    #print(f"{tx_message.arbitration_id:X}: {tx_message.data}")
  
                time.sleep(0.001)                       # Wait for 1s before updating
            except Exception as e:
                print(f"Exception: {e}") 
                if(toggle < 10): 
                    toggle = toggle +1 
                    print(f"{numMissing}")
                    #print(float(row[1]))

                #time.sleep(sample_time) 
                #print("in except")
                #print(numMissing)
                continue

                


            