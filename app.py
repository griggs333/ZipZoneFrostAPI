import numpy as np
from flask import Flask, render_template, url_for, request, redirect
# from flask_wtf import FlaskForm
# from wtforms import validators, SelectField
# import requests as req
# from bs4 import BeautifulSoup
import os
from flask_pydantic import validate
from pydantic import BaseModel, Field
from typing import Annotated
import requests
# import gunicorn_conf

app = Flask(__name__)


class ZipCode(BaseModel):
    zip: Annotated[str, Field(strip_whitespace=True), Field(min_length=5), Field(max_length=10), Field(pattern=r'^\d{5}(-\d{4})?$')]

class NoaaAPICall:
    def __init__(self):
        self.datasetid = 'datasetid=NORMAL_ANN'
        self.locationid = ''
        self.datacategoryid = ''
        self.datatypeid = ['ANN-TMIN-PRBLST-T32FP20', 'ANN-TMIN-PRBLST-T32FP50', 'ANN-TMIN-PRBLST-T32FP80']
        self.extent = ''
        self.startdate = "startdate=2010-01-01"
        self.enddate = "enddate=2010-01-01"
        self.units = ''
        self.sortfield = ''
        self.sortorder = ''
        self.limit = 'limit=5'
        self.offset = ''
        self.lat = ''
        self.lon = ''
        self.stationid = ''
        self.includemetadata = "includemetadata=false"
        # self.spring_frost_twenty
        # self.spring_frost_fifty
        # self.spring_frost_eighty

    def zip_to_lat_lon(self):
        baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations?"
        payload = {}
        headers = {
            'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
        }

        url = baseUrl + self.locationid + "&" + self.limit + "&" + self.includemetadata

        response = requests.request("GET", url, headers=headers, data=payload)

        self.lat = response.json()["results"][0]["latitude"]
        self.lon = response.json()["results"][0]["longitude"]

        return self.lat, self.lon

    def lat_lon_to_stationid(self):
        baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations?"
        payload = {}
        headers = {
            'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
        }
        self.extent = "extent=" + str(float(self.lat)-0.5) + "," + str(float(self.lon)-0.5) + "," + str(float(self.lat)+0.5) + "," + str(float(self.lon)+0.5)

        url = baseUrl + self.datasetid + "&" + self.extent + "&" + self.limit

        response = requests.request("GET", url, headers=headers, data=payload)

        self.stationid = [response.json()["results"][x]["id"] for x in range(len(response.json()["results"]))]

        return self.stationid

    def noaa_data_api_call(self):
        baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/data?"
        payload = {}
        headers = {
            'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
        }

        url = baseUrl + self.datasetid + "&" + "datatypeid=" + self.datatypeid[0] + "&" + "stationid=" + self.stationid[0] + "&" + self.startdate + "&" + self.enddate

        response = requests.request("GET", url, headers=headers, data=payload)

        print(type(response.json()["results"]), response.json()["results"])
        parsed_results = [response.json()["results"][0]["datatype"], response.json()["results"][0]["value"]]
        # parsed_results = [[response.json()["results"][x]["datatype"], response.json()["results"][x]["value"]] for x in range(len(response.json()["results"]))]

        return parsed_results



# def noaa_station_finder(zip):
#
#     baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations?datasetid=NORMAL_ANN&extent=33.260038,-84.781608,34.1,-83.8"
#     datasetid = "NORMAL_ANN"
#     payload = {}
#     headers = {
#         'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
#     }
#
#     response = requests.request("GET", url, headers=headers, data=payload)

# def noaa_frostdate_call(stationids):
#     baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/data?datasetid=NORMAL_ANN&datatypeid=ANN-TMIN-PRBLST-T32FP20&datatypeid=ANN-TMIN-PRBLST-T32FP50&datatypeid=ANN-TMIN-PRBLST-T32FP80&startdate=2009-01-01&enddate=2019-01-01"
#
#     datasetid = "NORMAL_ANN"
#     datatypeid = ["ANN-TMIN-PRBLST-T32FP20", "ANN-TMIN-PRBLST-T32FP50", "ANN-TMIN-PRBLST-T32FP80"]
#     locationid = ""
#     stationid = ""
#     payload = {}
#     headers = {
#         'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
#     }
#
#     response = requests.request("GET", url, headers=headers, data=payload)


@app.route('/zipcode', methods={'POST', 'GET'})
@validate()
def get_zip(query: ZipCode):
    noaa = NoaaAPICall()
    noaa.locationid='locationid=ZIP:' + query.zip
    a = noaa.zip_to_lat_lon()
    b = noaa.lat_lon_to_stationid()
    c = noaa.noaa_data_api_call()
    print(a, b, c)
    return query





app.run(host='0.0.0.0', port=8080)
