import csv 
import os
import time

import cantools.database 
from CANBase import CANInterface

file_path = r'replay_log_2.1.csv'

#open and read csv file
with open(file_path, mode='r', newline='') as csvfile:
    reader = csv.reader(csvfile)


    from data.message_data import MessageData
    hfi_dbc = os.path.join(os.getcwd(), r'HardwareInjector.dbc')
    hfi_db = cantools.database.load_file(hfi_dbc)
    vcu_torque_dbc = os.path.join(os.getcwd(), r'M150_VCU_TORQUE.dbc')
    vcu_torque_db = cantools.database.load_file(vcu_torque_dbc)
    # mc_torque_dbc = os.path.join(os.getcwd(), r'Software\DBC Tools\20230411_Gen5_CAN_DBC_PantherRacing_2024_01_15.dbc')
    mc_torque_dbc = os.path.join(os.getcwd(), r'mc_test.dbc')
    mc_torque_db = cantools.database.load_file(mc_torque_dbc)
    print(vcu_torque_db)
    time.sleep(2)

    # Create the HFI messages
    hfi_command_mux0 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 0,
                                    'HARDINJ_output1Control': 0,
                                    'HARDINJ_output2Control': 0,
                                    'HARDINJ_output3Control': 127,
                                    'HARDINJ_output4Control': 200,
                                    'HARDINJ_output5Control': 200,
                                    'HARDINJ_output6Control': 200, 
                                })

    # create and start CAN interface 
    can_interface = CANInterface()
    # can_interface.start_send_and_update_100Hz()
    # # Add and send HFI messages
    # can_interface.add_message_100Hz(hfi_command_mux0)

    # Now we wait for a period of time for the systems to catch up
    time.sleep(1)

    # Now we test and compare 
    can_interface.start_receive_and_sort(can_db=mc_torque_db, timeout=2)
    time.sleep(1) #wait for systems to respond
    # value = can_interface.get_signal_from_dictionary('VCU_accuCoolantPressOut')

    for row in reader:
        loop_start_time = time.time()

        motor_rpm = can_interface.get_signal_from_dictionary('motorspeed')
        try:
            motor_rpm = abs(int(motor_rpm))
        except:
            motor_rpm=10000 #failsafe: we will reduce the torque to almost 0 in the event the rpm is not valid

        # Handle 0 rpm case
        # Default to the torque request
        if motor_rpm>0:
            try:
                power_replay_request = float(row[1])
            except Exception as e:
                power_replay_request = 0
                print(f"Power replay request invalid: {e}")

            torque_request = power_replay_request*9549.3/motor_rpm
            # print(power_replay_request)
            print(torque_request)
        else:
            try:
                torque_request = float(row[2])
            except Exception as e:
                print(f"Error reading torque from CSV:{e}")

        tp_request = torque_request/1.5

        tp_request = max(0, tp_request)
        tp_request = min(100, tp_request)
        hfi_command_mux0.data={
                                'HARDINJ_mux': 0,
                                'HARDINJ_output1Control': int((0.5+((tp_request/100)*4))*51),
                                'HARDINJ_output2Control': int((0.5+((tp_request/100)*4))*51),
                                'HARDINJ_output3Control': 127,
                                'HARDINJ_output4Control': 200,
                                'HARDINJ_output5Control': 200,
                                'HARDINJ_output6Control': 200,
                                }
        
        can_interface.send_can_message(can_id=hfi_command_mux0.message.frame_id, is_extended=False, data=hfi_command_mux0.encode_data())

        #calculate loop time and delay accordingly
        loop_elapsed_time = time.time() - loop_start_time
        time_to_sleep = 0.01 - loop_elapsed_time
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        else:
             print("Process took longer than 0.01ms")


    #Simulation is complete perform exit tasks
    print("SIMULATION COMPLETE")
    #We now set the TP to 0% to exit safely 
    hfi_command_mux0.data={
                                'HARDINJ_mux': 0,
                                'HARDINJ_output1Control': int((0.5+((0/100)*4))*51),
                                'HARDINJ_output2Control': int((0.5+((0/100)*4))*51),
                                'HARDINJ_output3Control': 127,
                                'HARDINJ_output4Control': 200,
                                'HARDINJ_output5Control': 200,
                                'HARDINJ_output6Control': 200,
                                }
        
    can_interface.send_can_message(can_id=hfi_command_mux0.message.frame_id, is_extended=False, data=hfi_command_mux0.encode_data())
    time.sleep(1)

    #end and close gracefully
    # can_interface.stop_receive_and_sort()
    # can_interface.stop_send_and_update_100hz()
    del can_interface
