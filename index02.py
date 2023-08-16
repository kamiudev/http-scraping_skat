import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime

# Define the API endpoint URL
url = "https://afgoerelsesdatabasen.dk/api/v1/portals/3a43ec60-bdcb-4b3e-96d6-8e424a906303/search"

results = []
year = 2008
month = 1
collection = None

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

            docUrl = 'https://afgoerelsesdatabasen.dk/api/Portals(3a43ec60-bdcb-4b3e-96d6-8e424a906303)/Documents/LocalPrimaryVariant/' + one['DocumentPath']
            response = requests.get(docUrl)
            soup = BeautifulSoup(response.text, 'html.parser')

            header = ""
            try:
                header = soup.select('section.indhold>p')[0].text
            except Exception as e:
                print(e)
                pass

            body = []
            body_soup = soup.select('section.toc')
            for one in body_soup:
                tmp = ""
                for p in one.find_all('p'):
                    tmp += p.text
                subtitle = ""
                try:
                    subtitle = one.find('h1').text
                except Exception as e:
                    print(e)
                    pass
                body.append({'title': subtitle , 'content': tmp})
            
            print(title)
            one = {'title': title, 'date': date, 'doctype': doctype,'header': header, 'body': body, 'timestamp': datetime.now()}
            # results.append(one)
            
            if collection.find_one({'title': title}) is None:
                collection.insert_one(one)
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

if __name__ == "__main__":  
    year = 2023
    connect_mongo()
    for month in range(1, 13):
        print ("{}{:02}".format(year, month))
        main()
    save_data()
    