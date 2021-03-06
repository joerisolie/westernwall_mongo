from flask import Flask
import os
import pymongo

app = Flask(__name__)
app.config.from_object('config')

app.mongo_client = pymongo.MongoClient(host=os.getenv('MONGO_HOST', 'ocp-ports.nithralas.local'), port=int(os.getenv('MONGO_PORT', '27017')), username=os.getenv('MONGO_USERNAME', None), password=os.getenv('MONGO_PASSWORD', None), replicaSet='rs0', readPreference='secondaryPreferred')

#app.mongo_client = pymongo.MongoClient(host=os.getenv('MONGO_HOST', 'localhost'), port=int(os.getenv('MONGO_PORT', '27017')), username=os.getenv('MONGO_USERNAME', None), password=os.getenv('MONGO_PASSWORD', None))

from app import views
from app.views import check_init_kvs

# Init kvs if necessary
check_init_kvs()
