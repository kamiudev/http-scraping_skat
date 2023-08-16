import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime

# Define the API endpoint URL
url = "https://www.retsinformation.dk/api/documentsearch"

results = []
lyear = 2008
hyear = 2008
month = 1
collection = None

def main():
    # Define the request payload
    # payload = {'page':{}, 'yh': 2020&yl=2020} 
    new_url = url + "?page=1&yl={}&yh={}".format(lyear, hyear)

    # Send a POST request with the payload as raw data
    response = requests.get(new_url)
    print(new_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the data from the response
        data = response.json()

        pageCount = data['pageCount']
        resultCount = data['resultCount']
        print (resultCount)

        for page in range(1, pageCount+1):
            new_url = url + "?page={}&yl={}&yh={}".format(page, lyear, hyear)
            response = requests.get(new_url)
            data = response.json()
            for one in data['documents']:
                docLink = "https://www.retsinformation.dk/api/document" + one['retsinfoLink']
                try:
                    body = requests.get(docLink).json()[0]
                except Exception as e:
                    print(e)
                    continue
                body['timestamp'] = datetime.now()
                body['documentType'] = one['documentType']
                body['dato'] = one['offentliggoerelsesDato']
                # if collection.find_one({'id': one['id']}) is None:
                collection.insert_one(body)
                print(one['shortName'])
        
        # print(len(data['Results']))
    else:
        print("Error: Failed to retrieve data from the API")

def connect_mongo():
    global collection
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["retsinformation"]
    collection = db["data_{}_{}".format(lyear, hyear)]

def save_json():
    # df = pd.DataFrame({'result' : results })
    # df.to_json('data.json')
    with open("data_{}.json".format(lyear), "w") as file:
        json.dump(results, file)

def save_csv():
    df = pd.DataFrame({'result': results})
    df.to_csv('data_{}.csv'.format(hyear), index=False, encoding='utf-8')

def save_data():
    # save_json()
    # save_csv()
    # save_mongo()
    pass

if __name__ == "__main__":  
    lyear = 1976
    hyear = 1980
    connect_mongo()
    main()
    
    