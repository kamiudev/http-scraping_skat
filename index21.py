import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from datetime import datetime
import logging
import sys

# Define the API endpoint URL
url = "https://api.cludo.com/api/v3/2073/10133/search"

results = []
collection = None
logger = logging.getLogger(__name__)

facets = [
    # {"Category": "Blanketter", "Subcategory": ["Borger", "Erhverv", "Jura", "Øvrige"]},
    {
        "Category": "Jura",
        "Subcategory": [
            # "Afgørelse",
            # "Bindende svar",
            # "Dom",
            # "Juridisk vejledning",
            # "Kendelse",
            # "Styresignal",
            # "Øvrige",
            "Øvrige afg.",
        ],
    },
    # {"Category": "Mest læste", "Subcategory": ["Borger", "Erhverv", "Jura", "Øvrige"]},
    # {"Category": "Øvrige", "Subcategory": ["Borger", "Erhverv", "Jura", "Øvrige"]},
]


def main(cat, subcat):
    global url
    perPage = 1000
    payload = {
        "ResponseType": "Json",
        "facets": {"Category": [cat], "Subcategory": [subcat]},
        "filters": {},
        "page": "1",
        "query": "*",
        "text": "",
        "sort": {},
        "rangeFacets": {},
        "perPage": perPage,
        "enableRelatedSearches": False,
        "applyMultiLevelFacets": True,
    }
    for page in range(1, 9982 // perPage + 2):
        payload["page"] = page

        # Send a POST request with the payload as raw data
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": "SiteKey MjA3MzoxMDEzMzpTZWFyY2hLZXk="},
        )

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the data from the response
            try:
                data = response.json()
            except Exception as e:
                msg = "page {} - Convert Json Error".format(page)
                logger.error(payload)
                # print(response.text)
                continue

            for one in data["TypedDocuments"]:
                body = one["Fields"]
                title = body["Title"]["Value"]
                one_url = body["Id"]["Value"]
                # MetaDescription = body['MetaDescription']['value']
                body["url"] = one_url
                body["timestamp"] = datetime.now()

                if collection.find_one({"url": one_url}) is None:
                    collection.insert_one(body)
                    # print(title)
                else:
                    msg = "url '{}'\n title '{}' - Content with the same title already exists.".format(
                        one_url, title
                    )
                    logger.error(msg)
                    print(msg)

            # print(len(data['Results']))
        else:
            print(url)
            print("Error: Failed to retrieve data from the API " + str(page))

        # response.close()


def connect_mongo():
    global collection, db
    client = MongoClient("mongodb://localhost:27017/")
    db = client["skat"]
    collection = db["data_10000"]


def save_json():
    pass


def save_csv():
    pass


def save_data():
    # save_json()
    # save_csv()
    # save_mongo()
    pass


def log_init():
    file_handler = logging.FileHandler("error_third_site_10000.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


if __name__ == "__main__":
    log_init()
    connect_mongo()

    for x in facets:
        cat = x['Category']
        for y in x['Subcategory']:
            if y[-1:] == '.': # when Subcategory is 'Øvrige afg.'
                collection = db["data_{}_{}".format(cat, y[:-1])]
            else :
                collection = db["data_{}_{}".format(cat, y)]
            main(cat, y)
    # main()
