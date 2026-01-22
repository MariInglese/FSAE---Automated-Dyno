import can
import cantools
import time

db = cantools.database.load_file('C:\\GitHub\\FSAE---Automated-Dyno\\Regression Code\\DBCs\\dyno_auto.dbc')

message = db.get_message_by_name('py_torque')

bus = can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=1000000)

def send_dyno_torque(torque_value, enable=1):        
    signals = {'torque': torque_value}

    data = message.encode(signals)

    msg = can.Message(arbitration_id=0x700, data=data, is_extended_id=False)
    bus.send(msg)

    time.sleep(0.01)


with open('C:\\GitHub\\FSAE---Automated-Dyno\\Regression Code\\CSVs\\real_csv.csv', mode='r') as csvfile:
    for row in csvfile:
        col = row.split(",")
        send_dyno_torque(float(col[1]))