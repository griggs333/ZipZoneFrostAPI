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

# import gunicorn_conf

app = Flask(__name__)


class ZipCode(BaseModel):
    zip: Annotated[str, Field(strip_whitespace=True), Field(min_length=5), Field(max_length=10), Field(pattern=r'^\d{5}(-\d{4})?$')]


@app.route('/zipcode', methods={'POST', 'GET'})
@validate()
def get_zip(query: ZipCode):
    return query





app.run(host='0.0.0.0', port=8080)
