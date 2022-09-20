import requests
import json
import random
import time


edgexip = '172.29.80.72'
volval=48
curval=30
vollevel=[0,48]
from concurrent.futures import ThreadPoolExecutor


def generateSensorData(volval, curval, vollevel):
    if volval==0: 
       volval=vollevel[random.randint(0,1)]
    else:
       volval=volval-1
    curval=random.randint(28 if curval-1<28 else curval-1, 32 if curval+1>32 else curval+1)
 
    print("AGV Values: Voltage- %s V, Current- %s A" % (volval, curval))

    return (volval, curval)


def post_urls(args):
    return requests.post(args[0], data=json.dumps(args[1]), headers=args[2], verify=args[3])
    
if __name__ == "__main__":

    sensorTypes = ["agv_voltage", "agv_current"]

    while(1):

        (volval, curval) = generateSensorData(volval, curval, vollevel)

        t=0
        
        while t<20:
         
         urls_list=[('http://%s:49986/api/v1/resource/Agv_Sensors_02/agv_voltage' % edgexip,volval,{'content-type': 'application/json'},False),('http://%s:49986/api/v1/resource/Agv_Sensors_02/agv_current' % edgexip,curval,{'content-type': 'application/json'},False),('http://%s:49986/api/v1/resource/Agv_Params_1/agv_power' % edgexip,volval*curval,{'content-type': 'application/json'},False)]
        
         t+=1

         with ThreadPoolExecutor(max_workers=3) as pool:
            response_list = list(pool.map(post_urls,urls_list))
        
         time.sleep(1)

