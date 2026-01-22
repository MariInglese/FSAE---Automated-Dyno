import can
import cantools
import time

db = cantools.database.load_file('20230411_Gen5_CAN_DBC_PantherRacing_2024_01_15.dbc')

message = db.get_message_by_name('M192_Command_Message')

bus = can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=1000000)

def send_dyno_torque(torque_value, enable=1):        
    signals = {
        'VCU_INV_Torque_Command': torque_value,
        'VCU_INV_Inverter_Enable': enable,
        'VCU_INV_Direction_Command': 1,
        'VCU_INV_Speed_Command': 0,
        'VCU_INV_Inverter_Discharge': 0,
        'VCU_INV_Speed_Mode_Enable': 0,
        'VCU_INV_Torque_Limit_Command': 100.0
    }

    data = message.encode(signals)

    msg = can.Message(arbitration_id=0x700, data=data, is_extended_id=False)
    bus.send(msg)

    time.sleep(0.01)


with open('Regression Code\CSVs\ramp_up.csv', mode='r') as csvfile:
    for row in csvfile:
        send_dyno_torque(float(row[1]))