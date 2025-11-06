
import time
import sys

import cantools
import os

# Get the parent directory path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

from CANBase import CANInterface

dbc_directory = os.path.join(os.getcwd(), 'Software\DBC Tools\HardwareInjector.dbc')
dbc_file = dbc_directory #'..\DBC Tools\output.dbc'
db = cantools.database.load_file(dbc_file)

def test_add_message_100Hz():
    from data.message_data import MessageData
    message = MessageData(message=db.get_message_by_name('HARDINJ_command'), 
                          data={
                                'HARDINJ_mux': 0,
                                'HARDINJ_output1Control': 127,
                                'HARDINJ_output2Control': 200,
                                'HARDINJ_output3Control': 200,
                                'HARDINJ_output4Control': 200,
                                'HARDINJ_output5Control': 200,
                                'HARDINJ_output6Control': 200,
                                }
    )

    message2 = MessageData(message=db.get_message_by_name('HARDINJ_command'), 
                          data={
                                'HARDINJ_mux': 0,
                                'HARDINJ_output1Control': 0,
                                'HARDINJ_output2Control': 10,
                                'HARDINJ_output3Control': 10,
                                'HARDINJ_output4Control': 10,
                                'HARDINJ_output5Control': 10,
                                'HARDINJ_output6Control': 10,
                                }
    )


    can_interface = CANInterface()
    can_interface.start_send_and_update_100Hz()
    # can_interface.send_and_update_can_message(can_id=message.frame_id, data=data, is_extended=False)
    # can_interface.send_and_update_can_message_100Hz(can_frame=message)
    can_interface.add_message_100Hz(message)
    time.sleep(2)
    can_interface.add_message_100Hz(message2)
    time.sleep(2)

    message2.data = {
                    'HARDINJ_mux': 0,
                    'HARDINJ_output1Control': 127,
                    'HARDINJ_output2Control': 200,
                    'HARDINJ_output3Control': 200,
                    'HARDINJ_output4Control': 200,
                    'HARDINJ_output5Control': 200,
                    'HARDINJ_output6Control': 200,
                    }

    can_interface.add_message_100Hz(message2)
    print(message2.encode_data())
    time.sleep(2)
    can_interface.stop_send_and_update_100hz()

def test_add_muxed_message():
    from data.message_data import MessageData
    message = MessageData(message=db.get_message_by_name('HARDINJ_command'), 
                          data={
                                'HARDINJ_mux': 0,
                                'HARDINJ_output1Control': 127,
                                'HARDINJ_output2Control': 0,
                                'HARDINJ_output3Control': 200,
                                'HARDINJ_output4Control': 200,
                                'HARDINJ_output5Control': 200,
                                'HARDINJ_output6Control': 200,
                                }
    )

    message2 = MessageData(message=db.get_message_by_name('HARDINJ_command'), 
                           data={
                                'HARDINJ_mux': 1,
                                'HARDINJ_output7Control': 0,
                                'HARDINJ_output8Control': 10,
                                'HARDINJ_output9Control': 10,
                                'HARDINJ_output10Control': 10,
                                'HARDINJ_output11Control': 10,
                                'HARDINJ_output12Control': 10,
                                }
    )

    message1_1 = MessageData(message=db.get_message_by_name('HARDINJ_command'),
                             data={
                                'HARDINJ_mux': 0,
                                'HARDINJ_output1Control': 127,
                                'HARDINJ_output2Control': 127,
                                'HARDINJ_output3Control': 127,
                                'HARDINJ_output4Control': 200,
                                'HARDINJ_output5Control': 200,
                                'HARDINJ_output6Control': 200,                                 
                                }
    )


    can_interface = CANInterface()
    can_interface.start_send_and_update_100Hz()
    # can_interface.send_and_update_can_message(can_id=message.frame_id, data=data, is_extended=False)
    # can_interface.send_and_update_can_message_100Hz(can_frame=message)
    can_interface.add_message_100Hz(message)
    time.sleep(2)
    can_interface.add_message_100Hz(message2)
    time.sleep(2)
    can_interface.add_message_100Hz(message1_1)
    time.sleep(2)

    message2.data = {
                    'HARDINJ_mux': 1,
                    'HARDINJ_output7Control': 0,
                    'HARDINJ_output8Control': 127,
                    'HARDINJ_output9Control': 127,
                    'HARDINJ_output10Control': 127,
                    'HARDINJ_output11Control': 10,
                    'HARDINJ_output12Control': 10,
                    }

    can_interface.add_message_100Hz(message2)
    time.sleep(2)
    can_interface.stop_send_and_update_100hz()


def test_receieve():
    can_interface = CANInterface()

    can_interface.start_receive_and_sort(can_db=db, timeout=2)

    time.sleep(2)

    can_interface.get_signal_from_dictionary('HARDINJ_output7Control')
    time.sleep(10)
    can_interface.get_signal_from_dictionary('HARDINJ_output7Control')
    time.sleep(2)




test_add_message_100Hz()
# test_add_muxed_message()
# test_receieve()

time.sleep(10)
# can_interface.__del__()