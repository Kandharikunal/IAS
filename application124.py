import threading
import time
import random
from _thread import *
import json
import requests
from flask import Flask, jsonify, Response, request
from pykafka import KafkaClient
import sys
from pykafka.common import OffsetType
import math
import os

IP="127.0.0.1"
PORT="8000"
ipPort=IP+":"+PORT
busID=sys.argv[1]


biometricID="Biom " +busID

attempt=1
attemptFlag=True
while (attempt<5 and attemptFlag):
    try:
        global kafkaTopicBio
        kafkaTopicBio=requests.get("http://"+ipPort+"/getKafkaTopic/"+biometricID)
        kafkaTopicBio=kafkaTopicBio.text
        attemptFlag=False
    except:
        print("Error in getting Biometric Kafka Topic from Sensor Manager")
    time.sleep(5)
    attempt+=1


attempt=1
attemptFlag=True
while (attempt<5 and attemptFlag):
    try:
        global kafkaTopicBus
        kafkaTopicBus=requests.get("http://"+ipPort+"/getKafkaTopic/"+busID)
        kafkaTopicBus=kafkaTopicBus.text
        attemptFlag=False
    except:
        print("Error in getting Bus Kafka Topic from Sensor Manager")
    time.sleep(5)
    attempt+=1


rate = 10
xf=10
yf=10
tempThreshold=33
lightThreshold=207
def get_fare(xi,yi):
    global xf, yf, rate
    print(xf,yf,xi,yi)
    fare=abs((xf+yf)-(xi+yi))*5 + 100
    print(fare)
    return fare


def sendSMS(board):
    #send sms
    print(board)

def getBusCurrentCor():
    client = KafkaClient(hosts='localhost:9092')
    for i in client.topics[kafkaTopicBus].get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True):
        data_json = i.value.decode()
        data = json.loads(data_json)
        cor= (data["GPS"])
        temp= (data["currentTemp"])
        lux= (data["currentLux"])
        return cor,temp,lux

def getBiometric():
    client = KafkaClient(hosts='localhost:9092')
    flag=True
    
    for i in client.topics[kafkaTopicBio].get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True):
        data_json = i.value.decode()
        print(data_json)
        data = json.loads(data_json)
        personId= (data["personID"])
        busCorrdinate,temp,lux=getBusCurrentCor()
        fare=get_fare(busCorrdinate[0],busCorrdinate[1])
        msg=personId + " has boarded Bus: "+str(busID)+" having fare: "+str(fare)
        sendSMS(msg)
        # if flag:
        #     flag=False
        if temp>tempThreshold:
            attempt=1
            attemptFlag=True
            while (attempt<5 and attemptFlag):
                try:
                    requests.get("http://"+ipPort+"/changeControllerState/"+busID+"/"+"switchACState"+"/True")
                    attemptFlag=False
                except:
                    print("Error in calling controller from Sensor Manager for Switching On AC")
                time.sleep(5)
                attempt+=1
        
        if lux<lightThreshold:
            attempt=1
            attemptFlag=True
            while (attempt<5 and attemptFlag):
                try:
                    requests.get("http://"+ipPort+"/changeControllerState/"+busID+"/"+"switchLightState"+"/True")
                    attemptFlag=False
                except:
                    print("Error in calling controller from Sensor Manager for Switching On Lights")
                time.sleep(5)
                attempt+=1
                
#getBiometric()




def getGPS():
    attempt=1
    attemptFlag=True
    while (attempt<5 and attemptFlag):
        try:
            global barricadesList
            barricadesList=requests.get("http://"+ipPort+"/getSensorData/"+"barricades")
            attemptFlag=False
        except:
            print("Error in calling Sensor Manager for getting barricades list")
        time.sleep(5)
        attempt+=1
    barricadesList=json.loads(json.loads(barricadesList.text))
    barricades=list()
    barricadesList=barricadesList["instances"]
    for b in barricadesList:
        barricades.append((float(b["X-cor"]),float(b["Y-cor"]),str(b["name"])))

    threshold=2

    client = KafkaClient(hosts='localhost:9092')
    for i in client.topics[kafkaTopicBus].get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True):
        data_json = i.value.decode()
        data = json.loads(data_json)
        cor= (data["GPS"])
        for bar in barricades:
            if math.sqrt(  (int(cor[0])-int(bar[0]))**2 + (int(cor[1])-int(bar[1]))**2     )<=threshold:
                barricadeName=bar[2]
                msg= str(busID)+ " has passed barricade "+str(barricadeName)
                print(msg)
                attempt=1
                attemptFlag=True
                while (attempt<5 and attemptFlag):
                    try:
                        requests.get("http://"+ipPort+"/sendNotification/"+msg)
                        attemptFlag=False
                    except:
                        print("Error in calling Sensor Manager for sending Notification for bus passing barricades")
                    time.sleep(5)
                    attempt+=1
                barricades.remove(bar)

                
# def forceStop():
#     while True:
#         with open("stop.txt", 'r') as f:
#             stopCondition=f.readline()
#             print(stopCondition)
#             if stopCondition=="true":
#                 os._exit(1)
#             time.sleep(3)


#application 1 and 2
biometricThread=threading.Thread(target=getBiometric,name="biometricThread")
biometricThread.start()

#application 4
gpsThread=threading.Thread(target=getGPS,name="gpsThread")
gpsThread.start()

# forceStopThread=threading.Thread(target=forceStop,name="forceStopThread")
# forceStopThread.start()