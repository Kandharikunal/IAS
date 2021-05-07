import pymongo
from pymongo import MongoClient
import json
import smtplib
cluster = MongoClient("mongodb+srv://SNSTeam:1234@mycluster.wrkyk.mongodb.net/IAS_Project?retryWrites=true&w=majority")

db = cluster["IAS_Project"]
sensor_class_collection = db["sensorClass"]
sensor_instance_collection = db["sensorInstance"]

# always have _db tag , it create bunch of dictionary associated with value
#post = {"_id": 1, "name": "lin", "score": 5}

#key is userId & value is Participant object
class DBHelper:
    def registerNewSensorClass(self,data):
        result=dict()
        success=""
        msg=""
        try:
            primaryKey={"_id":data.get("busClass")}
            # print(primaryKey)
            data.update(primaryKey)
            # print(data)
            try:
                sensor_class_collection.insert_one(data)
                success="True"
                msg="New Bus-class " + primaryKey["_id"]+"  registered successfully!!!"
                self.sendNotification("New busClass " + primaryKey["_id"]+" registered on platform","admin")
            except :
                success="False"
                msg="Sensor Class already present!!!!!"
                self.sendNotification("New busClass " + primaryKey["_id"]+" registration failed on platform","admin")
        except:
            success="False"
            msg="Sensor Class field is missing!!!!"
            self.sendNotification("New busClass " + primaryKey["_id"]+" registration failed on platform","admin")
        result["success_status"]=success
        result["msg"]=msg
        
        return str(result)
    

    def makeSensorInstances(self,data):
        data=data.get("instances")
        result=dict()
        allInstances=list()
        success=""
        msg=""
        for d in data:
            try:
                primaryKey={"_id":d.get("busId")}
                d.update(primaryKey)
                if self.checkIfsensorClassExists(d.get("busClass")):
                    try:
                        sensor_instance_collection.insert_one(d)
                        success="True"
                        msg="Sensor instance " + primaryKey["_id"]+" registered successfully!!!"
                        self.sendNotification("New sensor instance " + primaryKey["_id"]+" registrated on platform","admin")
                    except :
                        success="False"
                        msg="Sensor instance already present with ID: " + d.get("sensorId")
                        self.sendNotification("New sensor instance  " + primaryKey["_id"]+" registration failed on platform","admin")
                else:
                    success="False"
                    msg="Sensor class does not exists!!!!!!"
                    self.sendNotification("New sensor instance  " + primaryKey["_id"]+" registration failed on platform","admin")
            except:
                success="False"
                msg="Sensor Id field is missing!!!!"
                self.sendNotification("New sensor instance  " + primaryKey["_id"]+" registration failed on platform","admin")
            result["success_status"]=success
            result["msg"]=msg
            allInstances.append(result.copy())
        # self.sendNotification(str(allInstances))
        return str(allInstances)

    def checkIfsensorClassExists(self, key):
        results = sensor_class_collection.find({"_id":key})
        for result in results:
            if (key==result["_id"]):
                return True
        return False

    def checkIfsensorInstanceExists(self,key):
        results = sensor_instance_collection.find({"_id":key})
        for result in results:
            if (key==result["_id"]):
                return True
        return False

    def getInitialConfig(self,request):
        
        if request == "count":
            return str(sensor_instance_collection.count_documents({}))
        else :
            req,Id = request.split()
            # IX,IY,direc,magnitude,IP,portNo=config.text.split()
            primaryKey={"_id":Id}
            if self.checkIfsensorInstanceExists(Id):
                results = sensor_instance_collection.find({"_id":Id})
                for r in results:
                    IX = r["X-cor"]
                    IY = r["Y-cor"]
                    direc = r["direc"]
                    magnitude = r["magnitude"]
                    IP = r["ip"]
                    portNo = r["port"]
                    return  (IX + " "+ IY + " "+ direc + " "+ magnitude + " "+ IP + " "+ portNo)
            else:
                print("Bus instance " + Id + " is not present")
            

    
    def checkIfsensorClassAtLocationExists(self,sensorClass,location):
        results = sensor_instance_collection.find({"sensorClass":sensorClass, "location": location})
        for result in results:
            return result["sensorId"]
        return False

    
    def getSensorIdByLocation(self,data):
        data=data.get("requirement")
        result=dict()
        allInstances=list()
        success=""
        msg=""
        for d in data:
            try:
                primaryKey={"_id":d.get("sensorClass")}
                d.update(primaryKey)
                ID = self.checkIfsensorClassAtLocationExists(d.get("sensorClass"), d.get("location"))
                if ID:
                    success="True"
                    msg = ID
                else:
                    success="False"
                    msg="Sensor instance at location absent!!!"
            except:
                success="False"
                msg="Requirement field is missing!!!!"
            result["success_status"]=success
            result["msg"]=msg
            allInstances.append(result.copy()) 
        
        return str(allInstances)

    def validateAppSensors(self,data):
        data=data.get("classes")
        result=list()
        for d in data:
            result.append(self.checkIfsensorClassExists(d))
        return str(result)

    def getIpPortOfSensor(self,sensorId):
        results = sensor_instance_collection.find({"busId":sensorId})
        for result in results:
            return result["ip"]+":"+result["port"]
        return False

    def sendNotification(self,body,subject):
        
        sender='wtrending17@gmail.com'
        receiver='somyalalwani9@gmail.com'
        password='Kunal@iiit'
        smtpserver=smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(sender,password)
        print("****************************")
        print("receiver: ",receiver)
        print(body)
        print("*************************")
        if subject=="admin":
            msg='Subject:An activity occured on the platform\n'+str(body)
        else:
            msg='Subject:Bus Notification msg\n'+str(body)
        smtpserver.sendmail(sender,receiver,msg)
        print('Sent notification')
        smtpserver.close()


    def getAllBusInstances(self):
        #results = sensor_instance_collection.find({"sensorClass":sensorClass, "location": location})
        results = sensor_instance_collection.find({},{'_id':1})
        busIds=list()
        for result in results:
            busIds.append(result["_id"])
        print(busIds)
        return busIds




# db=DBHelper()
# db.getAllBusInstances()
# print(db.getInitialConfig("Bus Bus1"))
# print(db.getInitialConfig("count"))
# with open('jsons/busClass.json') as f:
#     data = json.load(f)
#     #print(data)
#     #print(type(data), "check type")
#     print(db.registerNewSensorClass(data))

# with open('jsons/busInstances.json') as f:
#     data = json.load(f)
    #print(data)
    #print(type(data), "check type")
    #print(db.makeSensorInstances(data))
    #print(db.getInitialConfig(data))


# with open('assets/userRequirement.json') as f:
# data = json.load(f)
# # print(data)
# print(db.getSensorIdByLocation(data))

# print(db.checkIfKeyExists("shaitan_temp5"))
# print(db.getIpPortOfSensor("S115"))