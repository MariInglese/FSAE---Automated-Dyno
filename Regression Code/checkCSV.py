# First column time
# Second column torque
file_path = r'real_csv.csv'

with open(file_path, mode='r', newline='') as csvfile:
    reader1 = csv.reader(csvfile)
    # Get time in between samples 
    first_row = next(reader1)
    print(first_row)
    second_row = next(reader1) 
    print(second_row)
    sample_time  = float(second_row[0]) - float(first_row[0]) # 0 is time, 1 is torque
with open(file_path, mode='r', newline='') as csvfile:
    reader2 = csv.reader(csvfile)
    # Iterate through CSV
    for row in reader2: 
        try: 
            torque = float(row[1])              # Fetch torque feedback
            print(torque)
            data = message.encode({'CMD_TargetAcCurrent': torque})  # Encode message
            tx_message = can.Message(arbitration_id=0x36, is_extended_id=False,
                        data=data)                # Formulate message
            bus.send(tx_message, timeout=0.2)      # Send message to BUS BUS BUS
            if tx_message is not None:
                print(f"{tx_message.arbitration_id:X}: {tx_message.data}")

            time.sleep(sample_time)                       # Wait for 1s before updating
        except: 
            print("in except")
            continue