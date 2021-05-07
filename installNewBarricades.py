import requests
import  json

with open('jsons/barricades.json') as f:
    data = json.load(f)
    url="http://127.0.0.1:5000/installNewBarricades/"+json.dumps(data)
    response = requests.get(url)
    print(str(response.json()))