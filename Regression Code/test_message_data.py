# import time
# import sys
# import os
# # Get the parent directory path
# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# # Add the parent directory to sys.path
# sys.path.insert(0, parent_dir)

# #import python libs
# import cantools

# #import custom libs
# from CANBase import CANInterface
# from data.message_data import MessageData

# #open dbc for use in testing 
# dbc_directory = os.path.join(os.getcwd(), 'Software\DBC Tools\output.dbc')
# dbc_file = dbc_directory #'..\DBC Tools\output.dbc'
# db = cantools.database.load_file(dbc_file)


# message = db.get_message_by_name('HARDINJ_command')
# message_data = {
#     'HARDINJ_mux': 0,
#     'HARDINJ_output1Control': 127,
#     'HARDINJ_output2Control': 200,
#     'HARDINJ_output3Control': 200,
#     'HARDINJ_output4Control': 200,
#     'HARDINJ_output5Control': 200,
#     'HARDINJ_output6Control': 200,
# }
# # data = message.encode({
# #     'HARDINJ_mux': 0,
# #     'HARDINJ_output1Control': 127,
# #     'HARDINJ_output2Control': 200,
# #     'HARDINJ_output3Control': 200,
# #     'HARDINJ_output4Control': 200,
# #     'HARDINJ_output5Control': 200,
# #     'HARDINJ_output6Control': 200,
# # })

# message_data_class = MessageData(message=message, data=message_data)
# message_data_class.encode_data()

# message_data_class = MessageData(message=db.get_message_by_name('HARDINJ_command'),
#                                  data={
#                                         'HARDINJ_mux': 0,
#                                         'HARDINJ_output1Control': 127,
#                                         'HARDINJ_output2Control': 127,
#                                         'HARDINJ_output3Control': 200,
#                                         'HARDINJ_output4Control': 200,
#                                         'HARDINJ_output5Control': 200,
#                                         'HARDINJ_output6Control': 200,
#                                     }
#                                 )
# message_data_class.encode_data()

# time.sleep(1)
