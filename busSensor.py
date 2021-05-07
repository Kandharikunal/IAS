#command line input: 
#python3 bus.py busid
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

busID = sys.argv[1]
logFileName="logs/"+busID+".log"
sleepTime=10
HYDERABAD_CORDINATE = [10,10]
app = Flask(__name__)



attempt=1
attemptFlag=True
while (attempt<5 and attemptFlag):
    try:
        global config
        config=requests.get("http://127.0.0.1:5000/getInitialConfig/"+"bus "+busID)
        attemptFlag=False
    except:
        print("Error in getting Initial Config details of Bus from Sensor Manager")
    time.sleep(5)
    attempt+=1




IX,IY,direc,magnitude,IP,portNo=config.text.split()
portNo=int(portNo)

if logUtility.checkLogFileExists(logFileName):
    with open(logFileName, 'r') as f:
        last_line = f.readlines()[-1]
        last_line=json.loads(last_line)

        IX=float(last_line["GPS"][0])
        IY=float(last_line["GPS"][1])
        currentTemp=last_line["currentTemp"]
        tempState=last_line["tempState"]
        currentLux=last_line["currentLux"]
        lightState=last_line["lightState"]
        buzzerState=last_line["buzzerState"]
else:
    IX=float(IX)
    IY=float(IY)
    currentTemp=random.randint(30,35)
    tempState=False
    currentLux=random.randint(200,210)
    lightState=False
    buzzerState=False

def switchOnGPS():
    flag=True
    kafkaStream()
    while flag:
        time.sleep(sleepTime)
        global IX,IY,tempState,lightState,currentTemp,currentLux
        
        if magnitude=="inc":
            if direc=="X":
                IX+=1
            elif direc=="Y":
                IY+=1
            elif direc=="XY":
                IX+=1
                IY+=1
        else:
            if direc=="X":
                IX-=1
            elif direc=="Y":
                IY-=1
            elif direc=="XY":
                IX-=1
                IY-=1
        if tempState==False:
            currentTemp=random.randint(30,35)
        if lightState==False:
            currentLux=random.randint(200,210)
        
        if IX == HYDERABAD_CORDINATE[0] and IY == HYDERABAD_CORDINATE[1]:
            flag=False
        kafkaStream()
    return  

def kafkaStream():
    global busID,IX,IY,currentTemp,tempState,currentLux,lightState,buzzerState
    topicName = busID
    client = KafkaClient(hosts='localhost:9092')
    topic = client.topics[topicName]
    producer = topic.get_sync_producer()
    i = 0
    while True:
        dict = {'GPS' : (IX,IY), 'tempState' : tempState, 'currentTemp' : currentTemp,'lightState':lightState,'currentLux':currentLux,'buzzerState':buzzerState}
        dict_json = json.dumps(dict)
        producer.produce(dict_json.encode())
        print(dict_json)
        with open(logFileName, 'a+') as file:
            print()
            file.write(dict_json)
            file.write("\n")
        return

@app.route('/switchACState/<val>')
def switchACState(val):
    global tempState,currentTemp
    tempState=True
    currentTemp=random.randint(15,20)
    return "ok"

@app.route('/switchLightState/<val>')
def switchLightState(val):
    global lightState,currentLux
    lightState=True
    currentLux=random.randint(500,510)
    return "ok"

@app.route('/switchBuzzerState/<val>')
def switchBuzzerState(val):
    global buzzerState
    buzzerState=eval(val)
    return "ok"

gpsThread=threading.Thread(target=switchOnGPS,name="gpsThread")
gpsThread.start()


if __name__ == '__main__':
    # global IP,portNo
    app.run(host=str(IP),port = int(portNo))
    
