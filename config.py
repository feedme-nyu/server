import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    """Base configuration."""
    TESTING = False 
    DEBUG = True
    SECRET_KEY = 'my precious'
    WEBSITE_NAME = 'Feed Me'
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')  #  fetch the google api key from .env
    YELP_API_KEY = os.environ.get('YELP_API_KEY')
   

