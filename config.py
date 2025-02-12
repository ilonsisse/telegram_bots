import os

from dotenv import load_dotenv
from os import getenv

load_dotenv('.env')
token = os.getenv('API_KEY')
