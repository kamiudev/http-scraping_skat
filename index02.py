import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime
import sys
import logging

# Define the API endpoint URL
url = "https://afgoerelsesdatabasen.dk/api/v1/portals/3a43ec60-bdcb-4b3e-96d6-8e424a906303/search"
readme_url = "https://docs.google.com/document/d/1dJQ3GaH9KxoQM8ZJWU7_J9Qut9rRfiW5ug_vF9XHNgU/edit"

results = []
collection = None
logger = logging.getLogger(__name__)

def main():
    # Define the request payload
    payload = {"fieldSetName":"SearchResultFields","page":1,"ordering":{"fieldName":"date_release","descending":True},"slices":True,"snippets":True,"skip":0,"take":1000,"criteria":{"status":["Effective"],"AFGLSR":["{}{:02}".format(year, month)]}} 

    # Send a POST request with the payload as raw data
    response = requests.post(url, json=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the data from the response
        data = response.json()
        # print(data)
        for one in data['Results']:
            date = one['date_release'] 
            doctype = one['document_type']
            title = one['title']

            try:
                docUrl = 'https://afgoerelsesdatabasen.dk/api/Portals(3a43ec60-bdcb-4b3e-96d6-8e424a906303)/Documents/LocalPrimaryVariant/' + one['DocumentPath']
                response = requests.get(docUrl)
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                msg = "title '{}' - Failed to retrieve data from the API.".format(title)
                logger.error(msg)
                print(msg)
                pass

            header = ""
            try:
                for one in soup.select('section.indhold>p'):
                    header += one.text + '\n'
            except Exception as e:
                msg = "title '{}' - header does not exist.".format(title)
                logger.error(msg)
                print(msg)
                pass

            body = []
            body_soup = soup.select('section.toc')
            for one in body_soup:
                (subtitle, tmp) = ('', '')
                try:
                    subtitle = one.find('h1').text
                except Exception as e:
                    msg = "title '{}' - An error occurred while reading the subtitle.".format(title)
                    logger.error(msg)
                    print(msg)
                    pass

                try:
                    for p in one.find_all('p'):
                        tmp += p.text + '\n'
                except Exception as e:
                    msg = "title '{}' - An error occurred while reading the contents.".format(title)
                    logger.error(msg)
                    print(msg)
                    pass

                body.append({'title': subtitle , 'content': tmp})
            
            # print(title)
            one = {'title': title, 'date': date, 'doctype': doctype,'header': header, 'body': body, 'timestamp': datetime.now()}
            # results.append(one)
            
            if collection.find_one({'title': title}) is None:
                collection.insert_one(one)
            else:
                msg = "title '{}' - Content with the same title already exists.".format(title)
                logger.error(msg)
                print(msg)
    else:
        print("Error: Failed to retrieve data from the API")

def connect_mongo():
    global collection
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["afgoerelsesdatabasen"]
    collection = db["data_{}".format(year)]

def save_json():
    # df = pd.DataFrame({'result' : results })
    # df.to_json('data.json')
    with open("data_{}.json".format(year), "w") as file:
        json.dump(results, file)

def save_csv():
    df = pd.DataFrame({'result': results})
    df.to_csv('data_{}.csv'.format(year), index=False, encoding='utf-8')

def save_data():
    # save_json()
    # save_csv()
    # save_mongo()
    pass

def getYearFromArg():
    if (len(sys.argv) < 2) :
        return 2023
    year = int(sys.argv[1])
    if year is None:
        year = 2023
    if year < 2007 or year > 2023:
        year = 2023
    return year

def log_init():
    file_handler = logging.FileHandler('error_first_site_{}.log'.format(year))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

if __name__ == "__main__":
    year = getYearFromArg()
    log_init()
    connect_mongo()
    for month in range(1, 13):
        print ("{}{:02}".format(year, month))
        main()
    save_data()
    