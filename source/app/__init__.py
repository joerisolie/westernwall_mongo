from flask import Flask
import os
import etcd

app = Flask(__name__)
app.config.from_object('config')

app.etcd_client = etcd.Client(host=os.getenv('ETCD_HOST', 'localhost'), port=int(os.getenv('ETCD_PORT', '4001')))

from app import views
from app.views import check_init_kvs

# Init kvs if necessary
check_init_kvs()
