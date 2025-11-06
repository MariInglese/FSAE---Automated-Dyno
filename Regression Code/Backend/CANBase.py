import can 
import time
import threading
import logging
import cantools
import cantools.database

from data.message_data import MessageData

class CANInterface:
    def __init__(self):
        # create a bus instance using 'with' statement,
        # this will cause bus.shutdown() to be called on the block exit;
        # many other interfaces are supported as well (see documentation)
        self.bus = can.interface.Bus(interface='pcan',
                    channel='PCAN_USBBUS2',
                    bitrate = 1000000,
                    receive_own_messages=True)
        

        #100Hz send thread
        self.is_sending = False
        self.message_list_100Hz = []
        self.message_list_100Hz_lock = threading.Lock()
        self.message_list_100Hz_isRunning = False
        self.send_and_update_100hz_thread = threading.Thread(target=self._send_and_update_can_message_100Hz)

        #receive signal dictionary
        self.receive_dictionary = {}
        self.receive_dictionary_lock = threading.Lock()
        self.receive_dictionary_isRunning = False
        self.receive_dictionary_thread = threading.Thread(target=self._receive_and_sort)
    
    def __del__(self):

        if self.is_sending:    
            self.is_sending=False
            if self.send_and_update_thread:
                self.send_and_update_thread.join()
                
        if self.message_list_100Hz_isRunning:
            self.message_list_100Hz_isRunning = False
            if self.send_and_update_100hz_thread:
                self.send_and_update_100hz_thread.join()

        self.bus.shutdown()

    '''
    Send can message funciton will send a singular CAN message with the parameters specified
    @can_id: the CAN ID of the message you want to send
    @is_extended: whether the ID uses extended messaging or not 
    @return: None
    '''
    def send_can_message(self, can_id, is_extended, data):
        self.message = can.Message(arbitration_id=can_id, is_extended_id=is_extended,
                                data=data)
        self.bus.send(self.message, timeout=0.2)

    '''
    Internal send and update function
    This will run in send_and_update_100hz_thread
    @return: None
    '''
    def _send_and_update_can_message_100Hz(self):
        while self.message_list_100Hz_isRunning:
            with self.message_list_100Hz_lock:     
                for message in self.message_list_100Hz:
                    message_to_send = can.Message(arbitration_id=message.message.frame_id,
                                                  is_extended_id=message.message.is_extended_frame,
                                                  data=message.encode_data())
                    try:
                        self.bus.send(message_to_send)
                    except Exception as e:
                        logging.error(f"Send and Update Error: {e}")
                    time.sleep(0.01)
        # frame_array = 

    '''
    Start Sending CAN messages at 100Hz
    '''
    def start_send_and_update_100Hz(self):
        self.message_list_100Hz_isRunning = True
        self.send_and_update_100hz_thread.start()

    '''
    Stop Sending CAN messages at 100Hz
    '''
    def stop_send_and_update_100hz(self):
        if self.send_and_update_100hz_thread:
            self.message_list_100Hz_isRunning = False
            self.send_and_update_100hz_thread.join()



    '''
    Add 100Hz messages to the array to be sent

    @can_message: the cantools Message object that you want to send 
    '''
    def add_message_100Hz(self, can_message: MessageData):
        mux_updated = False

        if self.message_list_100Hz_isRunning:
            with self.message_list_100Hz_lock:
                
                #check if message doesnt exist in the array, if it doesnt append. If it does replace the message
                if not any(message.message.frame_id == can_message.message.frame_id for message in self.message_list_100Hz):
                    #if the message doesnt exist we dont need to worry about any mutiplexors so we just add the message
                    self.message_list_100Hz.append(can_message)
                    print(f"Appended {can_message.message.name} to 100Hz List")
                else:
                    # we will handle muiplexed messages sepeartely from the standard ones
                    # check if the message is multiplexed, if so we are going to look at whether the specific muxed message is already added
                    if can_message.message.is_multiplexed():
                        # if multipled loop through and find the matching frame_id
                        for i in range (len(self.message_list_100Hz)):
                            if self.message_list_100Hz[i].message.frame_id == can_message.message.frame_id:
                                # if frame_id is found then we can look for the multiplexor signal and then see if the value of the mux 
                                #   is the same as what we are trying to add. If it is we will replace that whole message
                                for signal in self.message_list_100Hz[i].message.signals:
                                    if signal.is_multiplexer:
                                        if self.message_list_100Hz[i].data[signal.name] == can_message.data[signal.name]:
                                            print("Found Mux signal in message, updating message")
                                            self.message_list_100Hz[i] = can_message
                                            mux_updated = True

                        # if we didnt find the frame and/or mux ID in the array we will add it to it  
                        if not mux_updated:
                            self.message_list_100Hz.append(can_message)
                            print("Mux signal not found in message, appending message")                          

                    # If its a standard meessage and was found in the array then we just update the message here
                    else:
                        for i in range (len(self.message_list_100Hz)):
                            if self.message_list_100Hz[i].message.frame_id == can_message.message.frame_id:
                                self.message_list_100Hz[i] = can_message
                                print(f"Updated {can_message.message.name} in 100Hz List")
                                break

                



    def send_and_update_can_message(self, can_id, is_extended, data):
        '''
        Start sending CAN messages at a constant rate

        :param can_id: CAN message ID
        :param is_extended: Is the CAN ID using extended messaging or not
        :param data: The payload of the CAN message
        :param rate: CAN message send rate in Hz
        '''

        if not self.is_sending:
            self.is_sending = True
            self.send_and_update_thread = threading.Thread(target=self._send_and_update_can_message, args=(can_id, is_extended, data))
            self.send_and_update_thread.start()

    def _send_and_update_can_message(self, can_id, is_extended, data):
        while self.is_sending:
            self.message = can.Message(arbitration_id=can_id, is_extended_id=is_extended,
                                data=data)
            print("AUTOSEND")
            try:
                self.bus.send(self.message)
            except Exception as e:
                logging.error(f"Send and Update Error: {e}")

            time.sleep(0.01)
    # def get_can_message():
    #     self.bus.
    def receive_can_message(self, signal_id, timeout=None):
        message = self.bus.recv(timeout=timeout)
        while message.arbitration_id != signal_id:
            message = self.bus.recv(timeout=timeout)       
        return message

    

    # TODO: Document the functions below
    def start_receive_and_sort(self, can_db:cantools.database, timeout):
        self.receive_dictionary_thread = threading.Thread(target=self._receive_and_sort, args=(can_db, timeout))
        self.receive_dictionary_isRunning = True
        self.receive_dictionary_thread.start()

    '''
    Stop Sending CAN messages at 100Hz
    '''
    def stop_receive_and_sort(self):
        if self.receive_dictionary_thread:
            self.receive_dictionary_isRunning = False
            self.receive_dictionary_thread.join()
    
    def _receive_and_sort(self, can_db:cantools.database, timeout):
        self.receive_dictionary = {}
        while self.receive_dictionary_isRunning:
            message = self.bus.recv(timeout=timeout)

            if message:
                try:
                    # Get the corresponding message object from the DBC
                    db_message = can_db.get_message_by_frame_id(message.arbitration_id)
                    
                    # Decode the message data
                    decoded_data = db_message.decode(message.data)
                    
                    # Check if the message is multiplexed
                    if db_message.is_multiplexed():
                        multiplexer_signal = None

                        for signal in db_message.signals:
                            if signal.is_multiplexer:
                                multiplexer_signal = signal.name
                                break

                        if multiplexer_signal:
                            # Get the current multiplexor value
                            multiplexer_value = decoded_data[multiplexer_signal]
                            
                            # Extract only the signals for the current multiplexor value
                            # print(f"Message is multiplexed with {multiplexer_signal}={multiplexer_value}")
                            for signal in db_message.signals:
                                if signal.multiplexer_ids is None or multiplexer_value in signal.multiplexer_ids:
                                    with self.receive_dictionary_lock:
                                        self.receive_dictionary[signal.name] = decoded_data[signal.name]

                    else:
                        # For non-multiplexed messages, store all signals
                        for signal_name, signal_value in decoded_data.items():
                            with self.receive_dictionary_lock:
                                self.receive_dictionary[signal_name] = signal_value
                
                    # print(f"Updated signal dictionary: {self.receive_dictionary}")

                except KeyError:
                    # print(f"Message with ID {hex(message.arbitration_id)} not found in DBC.")
                    pass

    def get_signal_from_dictionary(self, signal_name):
        if self.receive_dictionary_isRunning:
            with self.receive_dictionary_lock:
                try:
                    return_signal = self.receive_dictionary[signal_name]
                except KeyError as e:
                    print(f"Key Not found: {e}")
                    return_signal = 0
        # print(return_signal)
        return return_signal 




# canInterface = CANInterface()
# canInterface.send_can_message(can_id=0xA11, data=[0x11, 0x22, 0x33], is_extended=False)

# while True:
#     print(canInterface.receive_can_message())