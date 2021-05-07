'''
{
"starttime": "24:00 hours format",
"endtime": "24:00 hours format",
"recurring_bit" : 0/1,
"recurring_interval" : seconds in INT, 
"busname" : "string/buzzer/STOP:Busname",
}
'''
import socket
IP="127.0.0.1"
PORT=8092

sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd.connect((IP, PORT))
sockfd.send("2021-05-07 23:23:05*2021-05-07 23:25:55*0*10*Bus1".encode())  
resp = sockfd.recv(1024).decode()
print(resp)
x=""
with open("appArchit.py","r") as f:
    x+=f.read()
print(x)
sockfd.send(x.encode())
resp = sockfd.recv(1024).decode()
print(resp)
sockfd.close()