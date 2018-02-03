import os
import pymongo

from app import app,forms
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from .forms import MessageForm, colors, DBMigrateForm

class Message(object):
    name = ""
    message = ""
    rating = 0
    voters = 0
    color = colors[0][1]

    def __init__(self, name, message,rating,voters,color):
        self.message = message
        self.name = name
        self.rating = rating
        self.voters = voters
        self.color = color

    def asDict(self):
        return {
            'message' : self.message,
            'name' : self.name,
            'rating' : self.rating,
            'voters' : self.voters,
            'color' : self.color
        }

def check_init_kvs():
    # Check if keys exist in kvs
    coll = app.mongo_client['westernwall']['messages']
    qry_cnt = coll.find().count()
    if qry_cnt == 0:
        #Only if key not found (=new mongo instance) create 36 new messages.
        coll = app.mongo_client['westernwall']['messages']
        create_initial_messages(coll)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET','POST'])
@app.route('/index/<string:do_refresh>', methods=['GET','POST'])
def index(do_refresh=False):
    #check_init_kvs()
    form = MessageForm()

    db = app.mongo_client['westernwall']
    coll = db['messages']

    if form.validate_on_submit():
        try:
            flash("User %s posted message %s" % (form.name.data, form.message.data))
            res_color = "#FFFFFF"
            for c in colors:
                if form.color.data == c[0]:
                    res_color = c[1]
            m = Message(form.name.data,form.message.data,3,0,res_color)
            random_message = list(coll.aggregate([{ "$sample": {"size": 1}}]))
            coll.update_one({'_id': random_message[0].get('_id')}, {"$set": m.asDict()}, upsert=False)
        except Exception:
            flash("Something went wrong while posting your message.", 'error')

    messages = []
    try:
        for message in coll.find():
            messages.append(Message(message['name'], message['message'], message['rating'], message['voters'], message['color']))
    except pymongo.errors.ServerSelectionTimeoutError:
        flash("Something went wrong while getting the messages from the database.", 'error')

    return render_template('index.html', title='The Western Wall', messages=messages, form=form, do_refresh=do_refresh)

def create_initial_messages(coll):
    # Create 36 empty messages
    count = 0
    while count < 36:
        m = Message("", "", 3, 0, "#FFFFFF")
        coll.insert_one(m.asDict())
        count += 1

@app.route('/dbinit', methods=['GET'])
def dbinit():
    coll = app.mongo_client['westernwall']['messages']

    #Delete all keys
    coll.delete_many({})

    create_initial_messages(coll)

    return "DB initiated"

@app.route('/ipcheck')
def ipcheck():
    retvalue = os.popen("ip addr show").readlines()
    yourip = request.remote_addr
    ip_access_route = request.access_route
    return render_template('ipcheck.html', title='The Western Wall - IP Check', ipinfos = retvalue, yourip=yourip, ip_access_route=ip_access_route)

@app.route('/dbmigrate', methods=['GET','POST'])
def dbmigrate():
    form = DBMigrateForm()

    if form.validate_on_submit():
        db = app.mongo_client['westernwall']
        coll = db['messages']

        if not form.migratedata.data:
            flash("DB changed to %s:%s" % (form.hostname.data, form.port.data))
            app.mongo_client = pymongo.MongoClient(host=form.hostname.data,port=int(form.port.data))
        else:
            #Read all messages, change DB and write them to the new db
            messages = coll.find()
            app.mongo_client = pymongo.MongoClient(host=form.hostname.data, port=int(form.port.data))
            try:
                app.mongo_client['westernwall']['messages'].delete_many({})
                app.mongo_client['westernwall']['messages'].insert_many(messages)
            except pymongo.errors.BulkWriteError:
                flash("An error occurred while migrating the data to the new database, make sure the new database is empty.")

            flash("DB migrated to %s:%s" % (form.hostname.data, form.port.data))

    return render_template('dbmigrate.html', title='The Wester Wall - DB Migrate', form=form)
