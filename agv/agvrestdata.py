import requests
import json
import random
import time


edgexip = '172.29.80.72'
tempval = 25
speedval = 750
weightval = 125


def generateSensorData(tempval, speedval, weightval):

    tempval = random.randint(tempval-5, tempval+5)
    speedval = random.randint(0 if speedval-35<0 else speedval-35, 1500 if speedval+35>1500 else speedval+35)
    weightval = random.randint(0 if weightval-10<0 else weightval-10, 250 if weightval+10>250 else weightval+10)
 
    print("AGV Values: Temperature- %s C, Speed- %s mm/s, LoadWeight- %s kg " % (tempval, speedval, weightval))

    return (tempval, speedval, weightval)



if __name__ == "__main__":

    sensorTypes = ["agv_temperature", "agv_speed","agv_loadweight"]

    while(1):

        (tempval, speedval, weightval) = generateSensorData(tempval, speedval, weightval)

        url = 'http://%s:49986/api/v1/resource/Agv_Sensors_01/agv_temperature' % edgexip
        payload = tempval
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

        url = 'http://%s:49986/api/v1/resource/Agv_Sensors_01/agv_speed' % edgexip
        payload = speedval
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        
        url = 'http://%s:49986/api/v1/resource/Agv_Sensors_01/agv_loadweight' % edgexip
        payload = weightval
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

        time.sleep(5)
