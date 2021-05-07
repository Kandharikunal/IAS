from flask import Flask, jsonify, Response, request
import time
import requests
import json
import Dao as dao
import threading
import logUtility as logUtility

from pykafka import KafkaClient
from pykafka.common import OffsetType
import json
dataBaseHelper = dao.DBHelper()


app = Flask(__name__)
logFileName="logs/sensorManager.log"
global barricades

if logUtility.checkLogFileExists(logFileName):
    with open(logFileName, 'r') as f:
        last_line = f.readlines()[-1]
        global barricades
        barricades=last_line

@app.route('/registerNewSensorClass/<sensorDetails>')
def register_sensors(sensorDetails):
    y = eval(sensorDetails)
    #print("\n\n\nCHECKOUT SENSOR REGISTRATION", dataBaseHelper.registerNewSensorClass(y))
    #print(str(json.dumps(dataBaseHelper.registerNewSensorClass(y))))
    return str(json.dumps(dataBaseHelper.registerNewSensorClass(y)))


@app.route('/makeSensorInstances/<instanceDetails>')
def make_instances_of_sensors(instanceDetails):
    y = eval(instanceDetails)
    #print("\n\n\nCHECKOUT SENSOR INSTANCES", dataBaseHelper.makeSensorInstances(y))
    return str(json.dumps(dataBaseHelper.makeSensorInstances(y)))

@app.route('/getInitialConfig/<configDetails>')
def getInitialConfig(configDetails):
    #y = eval(instanceDetails)
    #print("\n\n\nCHECKOUT SENSOR INSTANCES", dataBaseHelper.makeSensorInstances(y))
    return (dataBaseHelper.getInitialConfig(configDetails))

@app.route('/getKafkaTopic/<topicId>')
def getKafkaTopic(topicId):
    length=len(topicId.split())
    if length==2:
        id,kafkaTopic=topicId.split()
        topicId=kafkaTopic+"_"+id
    return (topicId)


@app.route('/installNewBarricades/<barricadesList>')
def installNewBarricades(barricadesList):
    global barricades
    barricades=barricadesList
    with open(logFileName, 'a+') as file:
        file.write(barricades)
        file.write("\n")
    return str(json.dumps("True"))

@app.route('/getSensorData/<sensorID>')
def getSensorData(sensorID):
    if sensorID=="barricades":
        return str(json.dumps(barricades))
    elif sensorID=="coordinates":
        return str(json.dumps(busCoordinates))

@app.route('/sendNotification/<body>')
def sendNotification(body):
    dataBaseHelper.sendNotification(body,"administration")
    return "Sent"

@app.route('/changeControllerState/<sensorID>/<field>/<newValue>')
def changeControllerState(sensorID, field, newValue):
    ipPort=dataBaseHelper.getIpPortOfSensor(sensorID)
    url="http://"+ipPort+"/"+str(field)+"/"+str(newValue)
    print("url************************************88",url)
    response = requests.get(url)
    return "ok"

# @app.route('/getSensorIdByLocation/<sensorLocation>')
# def getSensorIdByLocation(sensorLocation):
#     y = eval(sensorLocation)
#     #print("\n\n\nCHECKOUT SENSOR BY LOCATION", dataBaseHelper.getSensorIdByLocation(y))
#     return dataBaseHelper.getSensorIdByLocation(y)




# @app.route('/validateAppSensors/<program_sensors>')
# def validateAppSensors(program_sensors):
#     y = eval(program_sensors)
#     #print("\n\n\nCHECKOUT SENSOR BY LOCATION", dataBaseHelper.validateAppSensors(y))
#     return dataBaseHelper.validateAppSensors(y)

def kafkaStream(busId):
    client = KafkaClient(hosts='localhost:9092')
    global busCoordinates
    busCoordinates=dict()
    for i in client.topics[busId].get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True):
        data_json = i.value.decode()
        data = json.loads(data_json)
        busCoordinates[busId]=(data["GPS"][0],data["GPS"][1])

def generateBusCordinates():
    countOfBuses= int(dataBaseHelper.getInitialConfig("count"))     
    for i in range (1,countOfBuses+1):
        param="Bus"+str(i)
        kafkaThread=threading.Thread(target=kafkaStream,name="kafkaThread",args=[param])
        kafkaThread.start()

@app.route('/getAllBusInstances')
def getAllBusInstances():
    result=dataBaseHelper.getAllBusInstances()
    return str(json.dumps(result))



generateBusCordinates()
if __name__ == '__main__':
    app.run(port = 5000)
