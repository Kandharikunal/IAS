import threading
import time
import random
from _thread import *
import json
import requests
from flask import Flask, jsonify, Response, request
from pykafka import KafkaClient
import sys
import logUtility as logUtility

attempt=1
attemptFlag=True
while (attempt<5 and attemptFlag):
    try:
        global config
        config=requests.get("http://127.0.0.1:5000/getInitialConfig/"+"count")
        attemptFlag=False
    except:
        print("Error in getting count from Initial Config of Sensor Manager")
    time.sleep(5)
    attempt+=1


count=int(config.text)

logFileName="logs/biometric.log"

if logUtility.checkLogFileExists(logFileName):  
    global i  
    with open(logFileName, 'r') as f:
        last_line = f.readlines()[-1]
        print("Hello Last Line: ",last_line)
        i=int(last_line)
        print("Reinitializing i :",i)
else:
    i=1

def kafkaStream(busID):
    topicName = busID+"_Biom"
    client = KafkaClient(hosts='localhost:9092')
    topic = client.topics[topicName]
    producer = topic.get_sync_producer()
    
    while True:
        global i
        personID="user_"+str(i)
        i+=1
        dict = {'busID' : busID, 'personID' : personID }
        dict_json = json.dumps(dict)
        producer.produce(dict_json.encode())
        print(topicName,dict_json)
        with open(logFileName, 'a+') as file:
            file.write(str(i))
            file.write("\n")
        time.sleep(random.randint(5,5))


for j in range (1,count+1):
    param="Bus"+str(j)
    kafkaThread=threading.Thread(target=kafkaStream,name="kafkaThread",args=[param])
    kafkaThread.start()

