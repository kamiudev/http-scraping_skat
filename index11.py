import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime
import logging
import sys

# Define the API endpoint URL
url = "https://www.retsinformation.dk/api/documentsearch"

results = []
lyear = 2008
hyear = 2008
month = 1
collection = None
logger = logging.getLogger(__name__)

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
                    msg = "title '{}' - An error occurred while reading the contents.".format(one['title'])
                    logger.error(msg)
                    print(msg)
                    continue

                body['timestamp'] = datetime.now()
                body['documentType'] = one['documentType']
                body['dato'] = one['offentliggoerelsesDato']

                body.pop("isSagsforlobPeriodValid")
                body.pop("editorialNotes")
                body.pop("alternativeMedia")
                body.pop("isReprint")
                body.pop("caseHistoryReferenceGroup")
                body.pop("geografiskDaekningId")
                body.pop("hasFobTags")
                body.pop("isHistorical")
                body.pop("documentFobTagGroup")
                body['url'] = docLink

                if collection.find_one({'shortName': one['shortName']}) is None:    
                    collection.insert_one(body)
                    print(one['shortName'])
                else:
                    msg = "shortName '{}' - Content with the same title already exists.".format(one['shortName'])
                    logger.error(msg)
                    print(msg)                
        
        # print(len(data['Results']))
    else:
        print("Error: Failed to retrieve data from the API")

def connect_mongo():
    global collection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["retsinformation"]
    collection = db["data_{}_{}".format(lyear, hyear)]

def save_json():
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

def log_init():
    file_handler = logging.FileHandler('error_second_site_{}_{}.log'.format(lyear, hyear))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def getYearFromArg():
    global lyear, hyear;
    if (len(sys.argv) < 3) :
        return
    lyear = int(sys.argv[1])
    hyear = int(sys.argv[2])
    if lyear > hyear:
        hyear = lyear

if __name__ == "__main__": 
    lyear = 1665
    hyear = 1990
    getYearFromArg()
    log_init()
    connect_mongo()
    main()
    
    