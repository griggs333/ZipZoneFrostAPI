import numpy as np
from flask import Flask, render_template, url_for, request, redirect, abort
import os
from flask_pydantic import validate
from pydantic import BaseModel, Field
from typing import Annotated
import requests
# import gunicorn_conf
import json
import datetime

app = Flask(__name__)

@app.errorhandler(500)
def internal_error(error):
    return {"error": "500 Internal Error"}


class ZipCode(BaseModel):
    zip: Annotated[str, Field(strip_whitespace=True), Field(min_length=5), Field(max_length=10), Field(pattern=r'^\d{5}(-\d{4})?$')]


class NoaaAPICall:
    def __init__(self):
        self.datasetid = 'NORMAL_ANN'
        self.locationid = ''
        self.datacategoryid = ''
        self.datatypeid = ['ANN-TMIN-PRBLST-T32FP20', 'ANN-TMIN-PRBLST-T32FP50', 'ANN-TMIN-PRBLST-T32FP80', "ANN-TMIN-PRBFST-T32FP20", "ANN-TMIN-PRBFST-T32FP50", "ANN-TMIN-PRBFST-T32FP80"]
        self.extent = ''
        self.startdate = "2010-01-01"
        self.enddate = "2010-01-01"
        self.units = ''
        self.sortfield = 'datatype'
        self.sortorder = ''
        self.limit = '5'
        self.offset = ''
        self.lat = ''
        self.lon = ''
        self.stationid = ''
        self.includemetadata = "false"
        self.spring20 = []
        self.spring50 = []
        self.spring80 = []
        self.fall20 = []
        self.fall50 = []
        self.fall80 = []

    def queryBuilder(self, parameter_list=None):
        query_string = ''
        if parameter_list is None:
            parameter_list = self.__dict__.keys()
        i_dict = self.__dict__
        for i in parameter_list:
            if isinstance(i_dict[i], list):
                for x in i_dict[i]:
                    query_string += str(i) + '=' + str(x) + "&"
            else:
                query_string += str(i) + '=' + str(i_dict[i]) + "&"

        return query_string[:-1]

    # NOAA API response crawler?
    # def results_crawler(self, results, key_list, limit):
    #     if isinstance(results, list):
    #         for x in results:
    #             for y in key_list:
    #                 if y in
    #     elif isinstance(results, dict):

    def zip_to_lat_lon(self):
        baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations?"
        payload = {}
        headers = {
            'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
        }
        query_string = self.queryBuilder(parameter_list=["locationid", "limit", "includemetadata"])
        url = baseUrl + query_string

        # print(url)

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
        lat_bound_deg = 0.5
        lon_bound_deg = 0.5
        self.extent = str(float(self.lat)-lat_bound_deg) + "," + str(float(self.lon)-lon_bound_deg) + "," + str(float(self.lat)+lat_bound_deg) + "," + str(float(self.lon)+lon_bound_deg)

        query_string = self.queryBuilder(parameter_list=["datasetid", "extent", "limit", "includemetadata"])
        url = baseUrl + query_string

        response = requests.request("GET", url, headers=headers, data=payload)

        self.stationid = [response.json()["results"][x]["id"] for x in range(len(response.json()["results"]))]

        # return self.stationid

    def noaa_data_api_call(self):
        #
        # Datatype Definitions:
        #   'ANN-TMIN-PRBLST-T32FP20': 20% probability date of last 32F occurrence or later
        #   'ANN-TMIN-PRBLST-T32FP50': 50% probability date of last 32F occurrence or later
        #   'ANN-TMIN-PRBLST-T32FP80': 80% probability date of last 32F occurrence or later
        #   "ANN-TMIN-PRBFST-T32FP20": 20% probability date of first 32F occurrence or earlier
        #   "ANN-TMIN-PRBFST-T32FP50": 50% probability date of first 32F occurrence or earlier
        #   "ANN-TMIN-PRBFST-T32FP80": 80% probability date of first 32F occurrence or earlier
        #

        def average_list(li):
            if len(li) < 1:
                return 0
            return round(sum(li) / len(li))

        #Temporary until response parser/crawler is written
        def append_spring_vals(results):
            spring20 = []
            spring50 = []
            spring80 = []
            fall20 = []
            fall50 = []
            fall80 = []

            for i in results:

                if i["datatype"] == "ANN-TMIN-PRBLST-T32FP20":
                    spring20.append(i["value"])

                elif i["datatype"] == "ANN-TMIN-PRBLST-T32FP50":
                    spring50.append(i["value"])

                elif i["datatype"] == "ANN-TMIN-PRBLST-T32FP80":
                    spring80.append(i["value"])

                elif i["datatype"] == "ANN-TMIN-PRBFST-T32FP20":
                    fall20.append(i["value"])

                elif i["datatype"] == "ANN-TMIN-PRBFST-T32FP50":
                    fall50.append(i["value"])
                    
                elif i["datatype"] == "ANN-TMIN-PRBFST-T32FP80":
                    fall80.append(i["value"])

            return spring20, spring50, spring80, fall20, fall50, fall80

        def value_to_date_conversion(value):
            start_date = datetime.datetime.strptime("01/01", "%m/%d")
            end_date = start_date + datetime.timedelta(days=value)

            return end_date.strftime("%m/%d")


        baseUrl = "https://www.ncei.noaa.gov/cdo-web/api/v2/data?"
        payload = {}
        headers = {
            'token': 'lJXcatwedWjNNDfeJMcluRTMxgkhNxLd'
        }

        query_string = self.queryBuilder(parameter_list=["datasetid", "datatypeid", "stationid", "startdate", "enddate", "includemetadata", "sortfield"])
        url = baseUrl + query_string
        print(url)

        response = requests.request("GET", url, headers=headers, data=payload)

        # with open("response.json", "w") as f:
        #     json.dump(response.json()["results"], f)

        try:
            self.spring20, self.spring50, self.spring80, self.fall20, self.fall50, self.fall80 = append_spring_vals(response.json()["results"])
        except:
            print("No frost dates found for this location")
            raise Exception("No frost dates found for this location")


        return {"Spring 20% Date": value_to_date_conversion(value=average_list(self.spring20)),
                "Spring 50% Date": value_to_date_conversion(value=average_list(self.spring50)),
                "Spring 80% Date": value_to_date_conversion(value=average_list(self.spring80)),
                "Fall 20% Date": value_to_date_conversion(value=average_list(self.fall20)),
                "Fall 50% Date": value_to_date_conversion(value=average_list(self.fall50)),
                "Fall 80% Date": value_to_date_conversion(value=average_list(self.fall80))
                }


@app.route('/zipcode', methods={'POST', 'GET'})
@validate()
def get_zip(query: ZipCode):

    noaa_api_call = NoaaAPICall()
    noaa_api_call.locationid = "ZIP:" + query.zip
    noaa_api_call.zip_to_lat_lon()
    noaa_api_call.lat_lon_to_stationid()

    temp_result = noaa_api_call.noaa_data_api_call()

    print(temp_result)
    return temp_result


@app.route('/500')
def error500():
    abort(500)


app.run(host='0.0.0.0', port=8080)
