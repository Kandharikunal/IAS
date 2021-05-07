# import os.path
# from os import path
# import json
# import  requests




# IP="127.0.0.1"
# PORT="8000"
# ipPort=IP+":"+PORT

# barricadesList=requests.get("http://"+ipPort+"/getSensorData/"+"barricades")
# barricadesList=json.loads(json.loads(barricadesList.text))
# barricades=list()
# barricadesList=barricadesList["instances"]
# for b in barricadesList:
#     barricades.append((float(b["X-cor"]),float(b["Y-cor"]),str(b["name"])))
# print(barricades)







# fileName1="logs/"+"Bus1"+".log"
# fileName2="logs/"+"Bus2"+".txt"
# fileName3="logs/"+"Bus3"+".txt"



# def checkLogFileExists(fileName):
#     if path.exists(fileName):
#         if (os.path.getsize(fileName) > 0):
#             return True
#         else:
#             return False
#     else:
#         return False

# print(checkLogFileExists(fileName1))
# print(checkLogFileExists(fileName2))
# print(checkLogFileExists(fileName3))

# if (checkLogFileExists(fileName1)):
#     with open(fileName1, 'r') as f:
#         last_line = f.readlines()[-1]
#         last_line=json.loads(last_line)
#         print(last_line["GPS"])
        
# else:
#     print("Bye")



import os

os.system("gnome-terminal -- python3 sensorManager.py")
os.system("gnome-terminal -- python3 Node.py")