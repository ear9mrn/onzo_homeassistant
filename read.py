#import datetime
import time, math, hid, os, requests
import onzo.device

conn = onzo.device.Connection()

try:

    conn.connect()
    disp = onzo.device.Display(conn)
    clamp = onzo.device.Clamp(conn)
    HASSIO_TOKEN = os.getenv('SUPERVISOR_TOKEN')

    p_reactive = None
    temp = clamp.get_temperature()
    counter = 0
    
    url_real = 'http://supervisor/core/api/states/sensor.onzo_energy'
    url_reac = 'http://supervisor/core/api/states/sensor.onzo_energy_reactive'
    url_app  = 'http://supervisor/core/api/states/sensor.onzo_energy_apparent'
    url_bat  = 'http://supervisor/core/api/states/sensor.onzo_energy_battery'
    url_temp = 'http://supervisor/core/api/states/sensor.onzo_energy_temp'
    url_kwh  = 'http://supervisor/core/api/states/sensor.onzo_energy_kwh'

    headers = {
       'Content-Type': 'application/json',
       'Authorization': f"Bearer {HASSIO_TOKEN}",
    }

 #print("Timestamp,P_real,P_reactive,P_apparent,kWh,Battery_Voltage,Temperature", flush=True)
    while True:
        p_real = clamp.get_power()

        # reactive power only updates onces every 15s, so there is no use
        # querying more often, this just wastes clamp battery
        if counter % 15 == 0:
            p_reactive = clamp.get_powervars()

        # Only update battery once every 10mins
        if counter % (60 * 10) == 0:
            battery = clamp.get_batteryvolts()
            temp = clamp.get_temperature()

        p_apparent = int(math.sqrt(p_real**2 + p_reactive**2))
        ear = clamp.get_cumulative_kwh()
        p_voltage = clamp.get_voltage()

        #timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print(f"{timestamp},{p_real},{p_reactive},{p_apparent},{ear},{battery},{temp}",flush=True)
        #print(f"{p_real},{p_reactive},{p_apparent},{ear},{battery},{temp},{p_voltage}",flush=True)    

 obj_real =  {'state': f"{p_real}", 'attributes': {'device_class' : 'power', 'unit_of_measurement': 'Watts', 'friendly_name': 'Onzo Monitor Current Usage'}}
        obj_reac =  {'state': f"{p_reactive}", 'attributes': {'device_class' : 'reactive_power', 'unit_of_measurement': 'var', 'friendly_name': 'Onzo Monitor Reactive Usage'}}
        obj_app  =  {'state': f"{p_apparent}", 'attributes': {'device_class' : 'apparent_power', 'unit_of_measurement': 'VA', 'friendly_name': 'Onzo Monitor Apparent Usage'}}
        obj_kwh  =  {'state': f"{ear}", 'attributes': {'device_class' : 'energy', 'unit_of_measurement': 'kWh', 'friendly_name': 'Onzo Monitor Usage kwh'}}
        obj_bat  =  {'state': f"{battery}", 'attributes': {'unit_of_measurement': 'Volts', 'friendly_name': 'Onzo Monitor Battery'}}
        obj_temp =  {'state': f"{temp}", 'attributes': {'device_class' : 'temperature', 'unit_of_measurement': '°C', 'friendly_name': 'Onzo Monitor Temperature'}}

        try:
           url_real_ret = requests.post(url_real, headers=headers, json = obj_real)
           url_temp_ret = requests.post(url_temp, headers=headers, json = obj_temp)

        except requests.exceptions.HTTPError as err:
           raise SystemExit(err)
           

        #print(url_real_ret.text, flush=True)

        counter += 1
        time.sleep(1)

finally:
    conn.disconnect()

