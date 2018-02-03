from flask_wtf import Form
from wtforms import StringField, TextAreaField, RadioField, BooleanField
from wtforms.validators import DataRequired, Length

colors = [(1, 'D93544'), (2, 'E7B632'), (3, 'F7E9CA'), (4, '31D99C'), (5, '32ACE1')]

class MessageForm(Form):
	name = StringField('name', validators=[DataRequired()])
	message = TextAreaField('message', validators=[DataRequired()])
	color = RadioField('color', choices=colors, coerce=int, validators=[DataRequired()])

class DBMigrateForm(Form):
	hostname = StringField('hostname', validators=[DataRequired()])
	port = StringField('port', validators=[DataRequired()], default="4001")
	migratedata = BooleanField('migratedata')