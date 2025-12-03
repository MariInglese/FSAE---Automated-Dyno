# Importing libraries 
import csv, os, time, math, can, cantools
import cantools.database 
from can.interfaces.pcan import pcan

# First column time
# Second column torque
file_path = r'real_csv.csv'
#write_file = w

numMissing = 0
toggle = 0 

#open and read csv file
dbc_directory = os.path.join(os.getcwd(), r'hv500_can2_map_v25_SID.dbc')
dbc_file = dbc_directory
db = cantools.database.load_file(dbc_file)

message = db.get_message_by_name('HV500_SetAcCurrent')

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
        for row in reader2: 
            numMissing = numMissing + 1
            try: 
                torque = float(row[1])              # Fetch torque feedback
                #print(torque)

                data = message.encode({'CMD_TargetAcCurrent': torque})  # Encode message
                tx_message = can.Message(arbitration_id=0x36, is_extended_id=False,
                            data=data)                # Formulate message
                bus.send(tx_message, timeout=0.2)      # Send message to BUS BUS BUS
                if tx_message is not None:
                    pass
                    #print(f"{tx_message.arbitration_id:X}: {tx_message.data}")
  
                #time.sleep(0.001)                       # Wait for 1s before updating
            except can.CanOperationError:
                time.sleep(.05)
                try:
                    bus.send(tx_message, timeout=.2)
                except:
                    numMissing += 1
                    continue
           
            # except Exception: 
            #     if(toggle < 10): 
            #         toggle = toggle +1 
            #         print(f"{numMissing}")
            #         print(f"{torque}")

            #     #time.sleep(sample_time) 
            #     #print("in except")
            #     continue

                


            