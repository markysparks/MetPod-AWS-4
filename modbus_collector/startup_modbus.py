import json
import logging
import os
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from threading import Timer
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient


class Datalogger:
    def __init__(self, mode, port, baud, tcp_ip, rate):
        self.qos = int(os.getenv('MQTT_QOS', 1))
        self.scanrate = rate

        # 'sensor': (Modbus ID, Modbus start address)
        self.sensor_array = {
            'winddir': (os.getenv('WINDDIR_ID', 1),
                        os.getenv('WINDDIR_REG', 7), True),
            'windspeed': (os.getenv('WINDSPEED_ID', 1),
                          os.getenv('WINDSPEED_REG', 5), True),
            'battvolts': (os.getenv('BATTVOLTS_ID', 1),
                          os.getenv('BATTVOLTS_REG', 1), True),
            'pressure': (os.getenv('PRESSURE_ID', 1),
                         os.getenv('PRESSURE_REG', 11), True),
            'tendency': (os.getenv('TENDENCY_ID', 1),
                         os.getenv('TENDENCY_REG', 13), True),
            'trend': (os.getenv('TREND_ID', 1),
                      os.getenv('TREND_REG', 15), True),
            'temperature': (os.getenv('TEMPERATURE_ID', 1),
                            os.getenv('TEMPERATURE_REG', 17), True),
            'temp2': (os.getenv('TEMP2_ID', 1),
                      os.getenv('TEMP2_REG', 19), True),
            'humidity': (os.getenv('HUMIDITY_ID', 1),
                         os.getenv('HUMIDITY_REG', 21), True),
            'dewpoint': (os.getenv('DEWPOINT_ID', 1),
                         os.getenv('DEWPOINT_REG', 23), True),
        }

        logging.info('ModBus mode requested = ' + mode)
        logging.info('ModBus scanrate requested = ' + str(rate) + 'secs')

        if mode == 'RTU':
            logging.info('ModBus RTU Serial port: ' + port)

            self.modbus_client = ModbusSerialClient(method='rtu',
                                                    port=port,
                                                    stopbits=1, bytesize=8,
                                                    parity='N',
                                                    baudrate=baud, timeout=5)
            logging.info('ModBus RTU connection established ' + port)

        elif mode == 'TCP':
            self.modbus_client = ModbusTcpClient(tcp_ip)
            logging.info('ModBus TCP connection established ' + tcp_ip)

        logging.info('Connecting to local MQTT broker....')
        self.connected = False  # variable for the state of the connection
        time.sleep(5)  # allow time for networking to be established
        self.client = mqtt.Client('modbus')  # create new instance
        self.client.on_connect = self.on_connect  # attach function to callback
        self.client.connect(
            os.getenv('MQTT_BROKER', 'localhost'))  # connect to broker
        self.client.loop_start()  # start the loop

        while not self.connected:  # Wait for connection
            time.sleep(0.1)

        self.modbus_scan()

        while True:
            time.sleep(1)

    def on_connect(self, mqtt_client, userdata, flags, rc):
        if rc == 0:
            # Connected
            logging.info('Connected to local MQTT broker')
            self.connected = True
        else:
            logging.info("MQTT Connection failed")

    def modbus_scan(self):
        message = {}
        try:
            self.modbus_client.connect()
            for sensor, config in self.sensor_array.items():
                if config[2]:
                    # logging.info(sensor + ' register: ' + str(config[1]))
                    data = payload_decode(
                        self.modbus_client.read_holding_registers(
                            int(config[1]), int(config[1]) + 1,
                            unit=int(config[0])))
                    logging.info(sensor + '= ' + str(data))
                    # Don't publish data fields with no data
                    if data != 'nan' and data is not None:
                        message.update({sensor: float(data)})
            self.modbus_client.close()
            obstime = (datetime.now(timezone.utc)).isoformat()
            message.update({'obstime': obstime})
            self.publish_mqtt(json.dumps(message))
            # Asynchronously schedule this function to run again in 1 seconds.
            Timer(self.scanrate, self.modbus_scan).start()
        except OSError as err:
            raise EnvironmentError(err)
            pass

    def publish_mqtt(self, data):
        self.client.publish('sensors/modbus', data, self.qos)


def payload_decode(instance):
    if not instance.isError():
        '''.isError() implemented in pymodbus 1.4.0 and above.'''
        decoder = BinaryPayloadDecoder.fromRegisters(instance.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Big
                                                     )
        return '{0:.2f}'.format(decoder.decode_32bit_float())

    else:
        # Error handling.
        logging.warning("The ModBus registers requested dont exist")
        return None


if __name__ == "__main__" and os.getenv('ENABLE', 'false') == 'true':
    logging.basicConfig(level=logging.INFO)
    logging.captureWarnings(True)
    logging.info('Starting ModBus data collector....')
    modbus_mode = os.getenv('MODBUS_MODE', 'TCP')
    rtu_port = os.getenv('RTU_PORT', '/dev/tty.usbserial-A9HDP06L')
    rtu_baud = int(os.getenv('RTU_BAUD', '115200'))
    tcp_address = os.getenv('TCP_ADDRESS', '192.168.1.5')
    modbus_scanrate = int(os.getenv('MODBUS_SCANRATE', '5'))
    Datalogger(modbus_mode, rtu_port, rtu_baud, tcp_address, modbus_scanrate)
