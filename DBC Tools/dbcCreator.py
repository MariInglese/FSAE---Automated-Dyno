import csv
import cantools
from cantools.database import Database, Message, Signal
from cantools.database.conversion import BaseConversion

# Function to convert a CSV row to a Signal object
def csv_row_to_signal(row):
    name = row['Signal Name']
    start = int(row['Start Bit'])
    length = int(row['Length'])
    byte_order = 'little_endian' if row['Byte Order'].lower() == 'little' else 'big_endian'
    is_signed = row['Signed'].lower() == 'true'
    factor = float(row['Scale'])
    offset = float(row['Offset'])
    minimum = float(row['Minimum']) if row['Minimum'] else None
    maximum = float(row['Maximum']) if row['Maximum'] else None
    unit = row['Unit']
    muxSignal = row['Multiplexer Signal']
    muxID = row['Multiplex ID']
    isMux = row['Is Multiplexor'].lower() == 'true'
    print(isMux)
    print(muxSignal)
    conversion = BaseConversion.factory(scale=factor, offset=offset)

    if muxID=='':
        muxID=None
    if muxSignal=='':
        muxSignal=None
    
    
    return Signal(
        name=name,
        start=(start+((length-1)%8)) if row['Byte Order'].lower() == 'big' else start,
        length=length,
        byte_order=byte_order,
        is_signed=is_signed,
        conversion=conversion,
        minimum=minimum,
        maximum=maximum,
        unit=unit,
        multiplexer_ids=muxID,
        multiplexer_signal=muxSignal,
        is_multiplexer=isMux
    )

# Initialize a new CAN database
db = Database()

# Read the CSV file
with open('test.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    
    messages = {}
    
    for row in reader:
        message_id = int(row['Message ID'], 16)
        message_name = row['Message Name']
        message_length = int(row['Message Length'])
        
        # Create or get the message
        if message_id not in messages:
            message = Message(
                frame_id=message_id,
                name=message_name,
                length=message_length,
                signals=[],
                cycle_time=100
            )
            messages[message_id] = message
            db.messages.append(message)
        else:
            message = messages[message_id]
        
        # Convert CSV row to Signal and add to the message
        signal = csv_row_to_signal(row)
        message.signals.append(signal)

# Save the database as a DBC file
with open('output.dbc', 'w') as f:
    f.write(db.as_dbc_string())
