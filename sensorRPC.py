import requests
import json


def registerNewSensorClass(sensorDetails):
    response = requests.get("http://127.0.0.1:5000/registerNewSensorClass/"+sensorDetails)
    return response


def makeSensorInstances(sensorInstances):
    response = requests.get("http://127.0.0.1:5000/makeSensorInstances/"+sensorInstances)
    return response


def getSensorIdByLocation(userRequirement):
    response = requests.get("http://127.0.0.1:5000/getSensorIdByLocation/"+userRequirement)
    return response


def validateAppSensors(program_sensors):
    response = requests.get("http://127.0.0.1:5000/validateAppSensors/"+program_sensors)
    return response


def getSensorData(sensorID, field):
    response = requests.get("http://127.0.0.1:5000/getSensorData/"+sensorID+"/"+field)
    return response


def changeControllerState(sensorID, field, newValue):
    response = requests.get("http://127.0.0.1:5000/changeControllerState/"+str(sensorID)+"/"+str(field)+"/"+str(newValue))
    return str(response)