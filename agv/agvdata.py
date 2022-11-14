import requests
import json
import random
import time


edgexip = '172.18.246.22'

volval=48
curval=30
tempval = 25
speedval = 1500
weightval = 0
vollevel=[0,48]
td = 0
tdp = 0

from concurrent.futures import ThreadPoolExecutor

def createSubscription():
    subscription={
  "channels": [
    {
      "mailAddresses": [
        "akash.m1@ltts.com",
        "sirisatwikakotha29@gmail.com"
      ],
      "type": "EMAIL"
    }
  ],
  "description": "Edgex Notification",
  "subscribedCategories": [
    "SECURITY"
  ],
  "subscribedLabels": [
    "metadata"
  ],
  "receiver":"Admin",
  "slug":"AGValert"
  }
    response = requests.post('http://%s:48060/api/v1/subscription' % \
                       edgexip,json=subscription,headers={'content-type': 'application/json'},verify=False)
    return response

def deleteSubscription():
    response = requests.delete('http://%s:48060/api/v1/subscription/slug/AGValert' % \
                       edgexip,headers={'content-type': 'application/json'},verify=False)
    return response
    
#def deleteNotification():
#    response = requests.delete('http://%s:48060/api/v1/notification/slug/AGValert' % \
#                       edgexip,headers={'content-type': 'application/json'},verify=False)
#    return response

def sendNotification(msg):
    notification = {
    "category": "SECURITY",
    "content": msg ,
    "description": "Alert regarding AGV",
    "labels": [
        "metadata"
    ],
    "sender": "edgex-kuiper",
    "severity": "CRITICAL",
    "slug": "AGValert",
    "status": "NEW"
    }
    response = requests.post('http://%s:48060/api/v1/notification' % \
                       edgexip,json=notification,headers={'content-type': 'application/json'},verify=False)
    return response

   
def generateVoltageData(volval, vollevel):
    if volval==0: 
       volval=vollevel[random.randint(0,1)]
    else:
       volval=volval-1
    return volval
       
def generateCurrentData(curval):       
    curval=random.randint(28 if curval-1<28 else curval-1, 32 if curval+1>32 else curval+1)

    return curval

def generateTemperatureData(tempval):
    tempval = random.randint(tempval-5, tempval+5)
    return tempval
    
def generateWeightData(weightval):
    weightval = random.randint(1,250)
    return weightval
    
def generateSpeedData(speedval,weightval):   
    speedval = 1500 - weightval
    return speedval
    
def post_urls(args):
    return requests.post(args[0], data=json.dumps(args[1]), headers=args[2], verify=args[3])
    
if __name__ == "__main__":

    sensorTypes = ["agv_temperature", "agv_speed","agv_loadweight","agv_voltage", "agv_current"]
    
    start_time=time.time()  
    
    flag = True  
    
    while(1):
       current_time = time.time()
       
       if current_time - start_time > 6000:
             break
             
       tw = time.time()
       
       if flag :
          weightval = generateWeightData(weightval)
       else:
          weightval = 0
        
       while time.time() - tw < 20:
          speedval = generateSpeedData(speedval, weightval)
          
          volval = generateVoltageData(volval,vollevel)
          
          curval = generateCurrentData(curval)
          
          tv = time.time()
          
          while time.time() - tv < 10:
               tempval = generateTemperatureData(tempval)
               
               #print(time.time() - tv)
               
               print("AGV Values: Temperature- %s C, Speed- %s mm/s, LoadWeight- %s kg Voltage- %s V, Current- %s A" % (tempval, speedval, weightval,volval, curval))
               
               urls_list=[('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' % edgexip,tdp,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' % edgexip,td,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % edgexip,"Available",{'content-type': 'application/json'},False) ]
               with ThreadPoolExecutor(max_workers=6) as pool:
                   response_list = list(pool.map(post_urls,urls_list))
                
               time.sleep(2) 
                               
               battery = (volval * 100)/48
               #print(tempval,battery)
               if (tempval > 40 or tempval<0) and  battery < 20 :
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % \
                   edgexip,data=json.dumps("Unavailable"),headers={'content-type': 'application/json'},verify=False)
                   td1 = time.time()
                   
                   createSubscription()
                   msg = 'Alert: AGV Temperature value is '+str(tempval)+' and Battery Levels are also low ('+str(battery)+')'
                   sendNotification(msg)
                   time.sleep(5)
                   
                   print("Inside condition1")
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_temperature' % \
                   edgexip,data=json.dumps(tempval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(3)
                   
                   if tempval > 40:
                       tempval = tempval//2
                   elif tempval < 0:
                       tempval = 25
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_temperature' % \
                   edgexip,data=json.dumps(tempval),headers={'content-type': 'application/json'},verify=False)
                     
                   while speedval>0:
                       if speedval-50<0 and speedval-100<0:
                          speedval = 0
                       else:
                          speedval = random.randint(0 if speedval-100<0 else speedval-100,0 if speedval-50<0 else speedval-50)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_Params_1/agv_speed' % \
                       edgexip,data=json.dumps(speedval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(5)
                       
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   urls_list=[ ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                   
                   td1=time.time()
                   
                   while volval < 48:
                       volval = random.randint(volval,volval+1)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_voltage' % \
                       edgexip,data=json.dumps(volval),headers={'content-type': 'application/json'},verify=False) 
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_Params_1/agv_distanceleft' % \
                       edgexip,data=json.dumps(speedval*72*(volval/480000)),headers={'content-type': 'application/json'},verify=False)
                       time.sleep(1)
                       
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   urls_list=[ ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                         
                   td1=time.time()
                   
                   while speedval<(1500-weightval):
                       if speedval+50>(1500-weightval) and speedval+100>(1500-weightval):
                          speedval=1500-weightval
                       else:
                          speedval = random.randint(1500-weightval if speedval+50>(1500-weightval) else speedval+50,1500-weightval if speedval+100>(1500-weightval) else speedval+100)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_speed' % \
                       edgexip,data=json.dumps(speedval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(5)
                       
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   td=td//2
                   tdp=tdp//2
                   
                   urls_list=[('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % edgexip,"Available",{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                   #deleteNotification()
                   deleteSubscription()
                                
               elif tempval > 40 or tempval < 0:
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % \
                   edgexip,data=json.dumps("Unavailable"),headers={'content-type': 'application/json'},verify=False)
                   td1 = time.time()
                   
                   createSubscription()
                   msg = 'Alert: AGV Temperature value is '+str(tempval)+' and Battery Levels are also low ('+str(battery)+')'
                   sendNotification(msg)
                   time.sleep(5)
                   
                   print("Inside condition 2")
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_temperature' % \
                   edgexip,data=json.dumps(tempval),headers={'content-type': 'application/json'},verify=False)
                   
                   time.sleep(3)
                   if tempval > 40:
                       tempval = tempval//2
                   elif tempval < 0:
                       tempval = 25
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_temperature' % \
                   edgexip,data=json.dumps(tempval),headers={'content-type': 'application/json'},verify=False)
                     
                   while speedval>0:
                       if speedval-50<0 and speedval-100<0:
                          speedval = 0
                       else:
                          speedval = random.randint(0 if speedval-100<0 else speedval-100,0 if speedval-50<0 else speedval-50)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_speed' % \
                       edgexip,data=json.dumps(speedval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(5)
                   
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   urls_list=[ ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                        
                   td1=time.time()
                   
                   time.sleep(5)
                   
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   urls_list=[ ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                         
                   td1=time.time()
                   
                   while speedval<(1500-weightval):
                       if speedval+50>(1500-weightval) and speedval+100>(1500-weightval):
                          speedval=1500-weightval
                       else:
                          speedval = random.randint(1500-weightval if speedval+50>(1500-weightval) else speedval+50,1500-weightval if speedval+100>(1500-weightval) else speedval+100)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_speed' % \
                       edgexip,data=json.dumps(speedval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(5)
                       
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   td=td//2
                   tdp=tdp//2
                   
                   urls_list=[('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % edgexip,"Available",{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                   #deleteNotification()
                   deleteSubscription()
               elif battery < 20 :
                   response = requests.post('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % \
                   edgexip,data=json.dumps("Unavailable"),headers={'content-type': 'application/json'},verify=False) 
                   td1 = time.time()
                   
                   createSubscription()
                   msg = 'Alert: AGV Temperature value is '+str(tempval)+' and Battery Levels are also low ('+str(battery)+')'
                   sendNotification(msg)
                   time.sleep(5)
                   
                   print('Inside condition 3')
                                        
                   while speedval>0:
                       if speedval-50<0 and speedval-100<0:
                          speedval = 0
                       else:
                          speedval = random.randint(0 if speedval-100<0 else speedval-100,0 if speedval-50<0 else speedval-50)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_temperature' % \
                       edgexip,data=json.dumps(tempval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(5)
                   
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   urls_list=[ ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list)) 
                       
                   td1=time.time()
                   
                   while volval < 48:
                       volval = random.randint(volval,volval+1)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_voltage' % \
                       edgexip,data=json.dumps(volval),headers={'content-type': 'application/json'},verify=False)
                       response = requests.post('http://%s:49986/api/v1/resource/Agv_Params_1/agv_distanceleft' % \
                       edgexip,data=json.dumps(speedval*72*(volval/480000)),headers={'content-type': 'application/json'},verify=False)
                       time.sleep(1)
                       
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   urls_list=[ ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                         
                   td1=time.time()
                   
                   while speedval<(1500-weightval):
                       if speedval+50>(1500-weightval) and speedval+100>(1500-weightval):
                          speedval=1500-weightval
                       else:
                          speedval = random.randint(1500-weightval if speedval+50>(1500-weightval) else speedval+50,1500-weightval if speedval+100>(1500-weightval) else speedval+100)
                          response = requests.post('http://%s:49986/api/v1/resource/Agv_01/agv_speed' % \
                          edgexip,data=json.dumps(speedval),headers={'content-type': 'application/json'},verify=False)
                   time.sleep(5)
                       
                   td1 = time.time() - td1
                   tr = time.time() - start_time
                   tdp = tdp + round((td1 * 100) / tr)
                   td = td + td1
                   
                   td=td//2
                   tdp=tdp//2
                   
                   urls_list=[('http://%s:49986/api/v1/resource/Agv_Params_1/agv_downtime' %edgexip,tdp,{'content-type': 'application/json'},False) ,\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_downtimeval' %edgexip,td,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False),\
                   ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_availability' % edgexip,"Available",{'content-type': 'application/json'},False) ]
                   with ThreadPoolExecutor(max_workers=6) as pool:
                       response_list = list(pool.map(post_urls,urls_list))
                   #deleteNotification()
                   deleteSubscription()
         
               tr = time.time() - start_time
                
               urls_list=[('http://%s:49986/api/v1/resource/Agv_01/agv_temperature' % edgexip,tempval,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_01/agv_speed' % edgexip,speedval,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_01/agv_loadweight' % edgexip,weightval,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_01/agv_voltage' % edgexip,volval,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_01/agv_current' % edgexip,curval,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_power' % edgexip,volval*curval,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_Params_1/agv_distanceleft' % edgexip,(speedval*72*(volval/480000)),{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_runtime' %edgexip,tr,{'content-type': 'application/json'},False),\
               ('http://%s:49986/api/v1/resource/Agv_Params_1_2/agv_uptimeval' %edgexip,(tr - td),{'content-type': 'application/json'},False)]
        
                
               with ThreadPoolExecutor(max_workers=6) as pool:
                   response_list = list(pool.map(post_urls,urls_list))
                   
               if (time.time() - tw)  >= 20:
                   flag= not flag    
                   
                   
#        "vijay.raichurkar@ltts.com",
#        "murali.krishna1@ltts.com"
