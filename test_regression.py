import math
import time

import cantools.database 
from CANBase import CANInterface

import cantools
import os
#dbc_directory = os.path.join(os.getcwd(), 'Software\DBC Tools\output.dbc')
#dbc_file = dbc_directory #'..\DBC Tools\output.dbc'
#db = cantools.database.load_file(dbc_file)

#message = db.get_message_by_name('HARDINJ_command')

#data = message.encode({
    #'HARDINJ_mux': 0,
    #'HARDINJ_output1Control': 127,
    #'HARDINJ_output2Control': 200,
    #'HARDINJ_output3Control': 200,
    #'HARDINJ_output4Control': 200,
    #'HARDINJ_output5Control': 200,
    #'HARDINJ_output6Control': 200,

#})

def test_test0():
    from data.message_data import MessageData
    hfi_dbc = os.path.join(os.getcwd(), 'HardwareInjector.dbc')
    hfi_db = cantools.database.load_file(hfi_dbc)
    #vcu_torque_dbc = os.path.join(os.getcwd(), 'Software\DBC Tools\M150_VCU_TORQUE.dbc')
    #vcu_torque_db = cantools.database.load_file(vcu_torque_dbc)

    # Create the HFI messages
    hfi_command_mux0 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 0,
                                    'HARDINJ_output1Control': 127,
                                    'HARDINJ_output2Control': 0,
                                    'HARDINJ_output3Control': 0,
                                    'HARDINJ_output4Control': 0,
                                    'HARDINJ_output5Control': 0,
                                    'HARDINJ_output6Control': 0, 
                                })

    # create and start CAN interface 
    can_interface = CANInterface()
    can_interface.start_send_and_update_100Hz()
    # Add and send HFI messages
    can_interface.add_message_100Hz(hfi_command_mux0)

    # Now we wait for a period of time for the systems to catch up
    time.sleep(10)
    del can_interface
    return 0

def start_CAN():
    can_interface = CANInterface()
    can_interface.send_can_message(can_id=message.frame_id, data=data, is_extended=False)
    can_interface.__del__()
    print("test")
    assert(True==True)

def test_sqrt():
    num = 25
    assert math.sqrt(25) == 5

def test_can():
    print(data)
    start_CAN()
    can_interface = CANInterface()
    can_interface.send_and_update_can_message(can_id=0x001, data=data, is_extended=False)
    time.sleep(10)
    can_interface.__del__()
    assert(True==True)

def test_strain_gauge_amp():
    dbc_directory = os.path.join(os.getcwd(), 'Strain Gauge DBC.dbc')
    dbc_file = dbc_directory #'..\DBC Tools\output.dbc'
    db = cantools.database.load_file(dbc_file)

    message = db.get_message_by_name('SGAMP1_data1000Hz')

    data = message.encode({
        'SGAMP1_outputVoltage': 5,
        'SGAMP1_ambientTemp': 100,
    })
    start_CAN()


def test_motor_pressure_sensors():
    from data.message_data import MessageData
    hfi_dbc = os.path.join(os.getcwd(), 'HardwareInjector.dbc')
    hfi_db = cantools.database.load_file(hfi_dbc)
    vcu_torque_dbc = os.path.join(os.getcwd(), 'M150_VCU_TORQUE.dbc')
    vcu_torque_db = cantools.database.load_file(vcu_torque_dbc)

    # Create the HFI messages
    hfi_command_mux0 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 0,
                                    'HARDINJ_output1Control': 127,
                                    'HARDINJ_output2Control': 127,
                                    'HARDINJ_output3Control': 127,
                                    'HARDINJ_output4Control': 200,
                                    'HARDINJ_output5Control': 200,
                                    'HARDINJ_output6Control': 200, 
                                })
    hfi_command_mux1 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 1,
                                    'HARDINJ_output7Control': 127,
                                    'HARDINJ_output8Control': 127,
                                    'HARDINJ_output9Control': 127,
                                    'HARDINJ_output10Control': 200,
                                    'HARDINJ_output11Control': 200,
                                    'HARDINJ_output12Control': 200, 
                                })

    # create and start CAN interface 
    can_interface = CANInterface()
    can_interface.start_send_and_update_100Hz()
    # Add and send HFI messages
    can_interface.add_message_100Hz(hfi_command_mux0)
    can_interface.add_message_100Hz(hfi_command_mux1)

    # Now we wait for a period of time for the systems to catch up
    time.sleep(1)

    # Now we test and compare 
    can_interface.start_receive_and_sort(can_db=vcu_torque_db, timeout=2)
    time.sleep(1) #wait for systems to respond
    value = can_interface.get_signal_from_dictionary('VCU_motorCoolantPressIn')
    time.sleep(1)
    # print(value)
    try:
        assert(475.0 <= value <= 525.0)
    finally:
        can_interface.stop_receive_and_sort()
        can_interface.stop_send_and_update_100hz()
        del can_interface



def test_accu_pressure_sensors():
    from data.message_data import MessageData
    hfi_dbc = os.path.join(os.getcwd(), 'HardwareInjector.dbc')
    hfi_db = cantools.database.load_file(hfi_dbc)
    vcu_torque_dbc = os.path.join(os.getcwd(), 'M150_VCU_TORQUE.dbc')
    vcu_torque_db = cantools.database.load_file(vcu_torque_dbc)

    tp_request = 50
    sendAnalog = int((0.5+((tp_request/100)*4))*51)
    # Create the HFI messages
    hfi_command_mux0 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 0,
                                    'HARDINJ_output1Control': 0, #unknown 
                                    'HARDINJ_output2Control': 0, #unknown 
                                    'HARDINJ_output3Control': sendAnalog, #APPS Main (AV3)
                                    'HARDINJ_output4Control': sendAnalog, #APPS Tracking (AV4)
                                    'HARDINJ_output5Control': 0, #INJ_LS1
                                    'HARDINJ_output6Control': 0, #AV6
                                })
    
    hfi_command_mux1 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 1,
                                    'HARDINJ_output7Control': sendAnalog, #AV7
                                    'HARDINJ_output8Control': 0,
                                    'HARDINJ_output9Control': 0,
                                    'HARDINJ_output10Control': 0,
                                    'HARDINJ_output11Control': 0,
                                    'HARDINJ_output12Control': 0, 
                                })
    

    # create and start CAN interface 
    can_interface = CANInterface()
    can_interface.start_send_and_update_100Hz()
    # Add and send HFI messages
    can_interface.add_message_100Hz(hfi_command_mux0)
    can_interface.add_message_100Hz(hfi_command_mux1)

    # Now we wait for a period of time for the systems to catch up
    time.sleep(1)

    # Now we test and compare 
    can_interface.start_receive_and_sort(can_db=vcu_torque_db, timeout=2)
    time.sleep(1) #wait for systems to respond
    value = can_interface.get_signal_from_dictionary('VCU_accuCoolantPressOut')
    try:
        assert(475.0 <= value <= 525.0)
    finally:
        print(value)
        can_interface.stop_receive_and_sort()
        can_interface.stop_send_and_update_100hz()
        del can_interface


def test_fail_accu_pressure_sensors():
    from data.message_data import MessageData
    hfi_dbc = os.path.join(os.getcwd(), 'Software\DBC Tools\HardwareInjector.dbc')
    hfi_db = cantools.database.load_file(hfi_dbc)
    vcu_torque_dbc = os.path.join(os.getcwd(), 'Software\DBC Tools\M150_VCU_TORQUE.dbc')
    vcu_torque_db = cantools.database.load_file(vcu_torque_dbc)

    # Create the HFI messages
    hfi_command_mux0 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 0,
                                    'HARDINJ_output1Control': 255,
                                    'HARDINJ_output2Control': 255,
                                    'HARDINJ_output3Control': 127,
                                    'HARDINJ_output4Control': 200,
                                    'HARDINJ_output5Control': 200,
                                    'HARDINJ_output6Control': 200, 
                                })
    hfi_command_mux1 = MessageData(message=hfi_db.get_message_by_name("HARDINJ_command"),
                                data={    
                                    'HARDINJ_mux': 1,
                                    'HARDINJ_output7Control': 127,
                                    'HARDINJ_output8Control': 127,
                                    'HARDINJ_output9Control': 127,
                                    'HARDINJ_output10Control': 200,
                                    'HARDINJ_output11Control': 200,
                                    'HARDINJ_output12Control': 200, 
                                })

    # create and start CAN interface 
    can_interface = CANInterface()
    can_interface.start_send_and_update_100Hz()
    # Add and send HFI messages
    can_interface.add_message_100Hz(hfi_command_mux0)
    can_interface.add_message_100Hz(hfi_command_mux1)

    # Now we wait for a period of time for the systems to catch up
    time.sleep(1)

    # Now we test and compare 
    can_interface.start_receive_and_sort(can_db=vcu_torque_db, timeout=2)
    time.sleep(1) #wait for systems to respond
    value = can_interface.get_signal_from_dictionary('VCU_accuCoolantPressOut')
    print(value)
    try:
        assert(475.0 <= value <= 525.0)
    finally:
        can_interface.stop_receive_and_sort()
        can_interface.stop_send_and_update_100hz()
        del can_interface
    
def test_hanger():
    assert(False)
    
