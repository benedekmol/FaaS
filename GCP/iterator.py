import time
import requests

def iterator(request):
    #Invoke function
    for i in range(100):
        url = "https://europe-west3-still-emissary-296814.cloudfunctions.net/invoker"
        headers = { "Content-Type" : "application/json", "Accept":"text/plain"}
        payload = {"id" : i , "mysqlWrite" : i}

        r = requests.post(url, json=payload)