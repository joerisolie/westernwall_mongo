import random
import os
import json
import etcd

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
	try:
		qry = app.etcd_client.read('/messages/', recursive=True)
	except etcd.EtcdKeyNotFound:
		#Only if key not found (=new etcd instance) create 36 new messages.
		count = 0
		#Create 36 empty messages
		while count < 36:
			m = Message("", "", 3, 0, "#FFFFFF")
			app.etcd_client.write('/messages/' + str(count), json.dumps(m.asDict()))
			count += 1

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET','POST'])
@app.route('/index/<string:do_refresh>', methods=['GET','POST'])
def index(do_refresh=False):
	check_init_kvs()
	form = MessageForm()

	if form.validate_on_submit():
		flash("User %s posted message %s" % (form.name.data, form.message.data))
		res_color = "#FFFFFF"
		for c in colors:
			if form.color.data == c[0]:
				res_color = c[1]
		m = Message(form.name.data,form.message.data,3,0,res_color)
		loc = random.randint(0,35)

		app.etcd_client.write('/messages/'+str(loc), json.dumps(m.asDict()))

	messages = []
	try:
		qry = app.etcd_client.read('/messages/', recursive = True)
		for x in range(0,36):
			x_value = next((y for y in qry.children if y.key == '/messages/'+str(x)), None)
			q_dict = json.loads(x_value.value)
			messages.append(Message(q_dict['name'], q_dict['message'], q_dict['rating'], q_dict['voters'], q_dict['color']))
	except etcd.EtcdKeyNotFound:
		flash("Something went wrong while getting the messages from etcd, is the directory initialized?", 'error')

	return render_template('index.html', title='The Western Wall', messages=messages, form=form, do_refresh=do_refresh)

@app.route('/dbinit', methods=['GET'])
def dbinit():
	#Delete all keys
	try:
		qry = app.etcd_client.read('/messages/', recursive=True)
		for q in qry.children:
			app.etcd_client.delete(q.key)
	except etcd.EtcdKeyNotFound:
		pass

	#Create 36 empty messages
	count = 0
	while count < 36:
		m = Message("", "", 3, 0, "#FFFFFF")
		app.etcd_client.write('/messages/' + str(count), json.dumps(m.asDict()))
		count += 1
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
		if not form.migratedata.data:
			flash("DB changed to %s:%s" % (form.hostname.data, form.port.data))
			app.etcd_client = etcd.Client(host=form.hostname.data, port=int(form.port.data))
		else:
			#Read all messages, change DB and write them to the new db
			messages = []
			try:
				qry = app.etcd_client.read('/messages/', recursive=True)
				for x in range(0, 36):
					x_value = next((y for y in qry.children if y.key == '/messages/' + str(x)), None)
					q_dict = json.loads(x_value.value)
					messages.append(
						Message(q_dict['name'], q_dict['message'], q_dict['rating'], q_dict['voters'], q_dict['color']))
			except etcd.EtcdKeyNotFound:
				flash("Something went wrong while getting the messages from etcd, is the directory initialized?",
					  'error')

			app.etcd_client = etcd.Client(host=form.hostname.data, port=int(form.port.data))

			for x in range(0, 36):
				app.etcd_client.write('/messages/' + str(x), json.dumps(messages[x].asDict()))

			flash("DB migrated to %s:%s" % (form.hostname.data, form.port.data))


		app.etcd_client = etcd.Client(host=form.hostname.data,port=int(form.port.data))

	return render_template('dbmigrate.html', title='The Wester Wall - DB Migrate', form=form)
