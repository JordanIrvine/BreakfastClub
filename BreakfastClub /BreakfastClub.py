from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, g
#from data import Articles
import sqlite3 as sql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#Index
@app.route('/')
def index():
	with sql.connect('test10.db') as connection:

		cur = connection.cursor()

		cur.execute("CREATE TABLE IF NOT EXISTS users (userId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name varchar(100) DEFAULT NULL,email varchar(100) DEFAULT NULL,username varchar(30) DEFAULT NULL,password varchar(100) DEFAULT NULL,register_date timestamp NOT NULL DEFAULT (datetime('now', 'localtime')))")
		# members
		cur.execute("CREATE TABLE IF NOT EXISTS members (clientId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name varchar(50) NOT NULL, author varchar(50) DEFAULT NULL, creationDate timestamp NOT NULL DEFAULT (datetime('now', 'localtime')))")
		# visits
		cur.execute("CREATE TABLE IF NOT EXISTS visits (visitId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,clientId int(11) DEFAULT NULL,breakfastDate timestamp NOT NULL DEFAULT (datetime('now', 'localtime')),author varchar(50) DEFAULT NULL, FOREIGN KEY(clientId) REFERENCES members(clientId))")
		# redeem
		cur.execute("CREATE TABLE IF NOT EXISTS redeem (redeemId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,clientId int(11) DEFAULT NULL,redeemDate timestamp NOT NULL DEFAULT (datetime('now', 'localtime')),author varchar(50) DEFAULT NULL,redeem tinyint(1) NOT NULL DEFAULT '0', FOREIGN KEY(clientId) REFERENCES members(clientId))")


		return render_template('home.html')

#Index
@app.route('/help')
def help():
	return render_template('help.html')

#Register form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message= 'Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

#User register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		with sql.connect('test6.db') as connection:

			connection.execute("INSERT INTO users(name, email, username, password) VALUES(?,?,?,?)", (name, email, username, password))

		flash('You are now registered and can now log in', 'success')

		redirect(url_for('index'))
	return render_template('register.html', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		with sql.connect('test10.db') as connection:

			# Get form fields
			username = request.form['username']
			password_candidate = request.form['password']
			#name = request.form['name']

			cur = connection.execute("SELECT * FROM users WHERE username = ?", (username,))

			result = cur.fetchone()

			if result is not None:

				data = result
				print('data[password]', data)
				password = data[4]

				#Compare Passwords
				if sha256_crypt.verify(password_candidate, password):
					#PasswordField
					session['logged_in'] = True
					session['username'] = username
					#session['name'] = name

					flash('You are now logged in', 'success')
					return redirect(url_for('memberSearch'))
				else:
					error = 'Invalid Login'
					return render_template('login.html', error=error)
				#close connection
			else:
				error = 'Username not found'
				return render_template('login.html', error=error)

	return render_template('login.html')


#Check if user is logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))


#memberSearch (Dashboard)
@app.route('/memberSearch')
@is_logged_in
def memberSearch():

	with sql.connect('test10.db') as connection:
		connection.row_factory = sql.Row
		cur = connection.execute("SELECT * from members m join visits v where v.breakfastDate = (select max(visits.breakfastDate) from visits where visits.clientId = m.clientId) UNION select * from members m left join visits v on m.clientId = v.clientId where breakfastDate is NULL")

		members = build_dict_list(cur)

		if members:
			return render_template('memberSearch.html', members=members)
		else:
			msg = 'No members Found'
			return render_template('memberSearch.html', msg=msg)

# Utility Functions
def build_dict_list(cur):
	dict_list = []

	nextElement = cur.fetchone()
	while nextElement is not None:
		dict_list.append(nextElement)
		nextElement = cur.fetchone()

	return dict_list

#Member Form class
class MemberForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])

#visitSearch (Dashboard)
@app.route('/visitSearch/<string:id>/', methods=['GET', 'POST'])
@is_logged_in
def visitSearch(id):

	with sql.connect('test10.db') as connection:
		connection.row_factory = sql.Row

		cur = connection.execute("SELECT * FROM visits WHERE clientId = ?", [id])

		result = cur.execute("SELECT * from members, visits WHERE members.clientId = ? AND visits.clientId = members.clientId", [id])
		visits = build_dict_list(cur)

		if visits:
			return render_template('visitSearch.html', visits=visits, name = visits[0]['name'])
		else:
			msg = 'No visits Found'
			return render_template('visitSearch.html', msg=msg)


# Add Visit
@app.route('/add_visit/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def add_visit(id):
	if request.method == 'POST':

		with sql.connect('test10.db') as connection:
			# Create Cursor
			cur = connection.cursor()

			clientId = [id]
			author = session['username']
			print(session['username'])

			# Execute
			cur.execute("INSERT INTO visits(clientId) VALUES(?)", (clientId),)

			cur.execute("SELECT * FROM visits WHERE clientId = ?", [id])

			#cur.execute("UPDATE members SET lastBreakfastDate = now() WHERE clientId = %s", [id])

			#cur.execute("UPDATE members SET leftTillFree =leftTillFree-1 WHERE clientId = %s", [id])

			#totalBreakfast = cur.execute("UPDATE members SET totalBreakfast = (COUNT(*) from visits WHERE clientId = %s", (clientId)))


			flash('Visit created', 'success')

		return redirect(url_for('memberSearch'))

# Add member
@app.route('/add_member', methods=['GET', 'POST'])
@is_logged_in
def add_member():
	form = MemberForm(request.form)
	if request.method == 'POST' and form.validate():

		with sql.connect('test10.db') as connection:

			name = form.name.data

			connection.execute("INSERT INTO members(name) VALUES(?)",[name],)

			flash('Member Created', 'success')

			return redirect(url_for('memberSearch'))

	return render_template('add_member.html', form=form)

# Delete Visit
@app.route('/delete_visit/<string:visitId>/<string:clientId>', methods=['POST'])
@is_logged_in
def delete_visit(visitId,clientId):

	with sql.connect('test10.db') as connection:

		cur = connection.cursor()

		visitId = [visitId]

		# Execute Delete
		cur.execute("DELETE FROM visits WHERE visitId = ?", (visitId),)

		return redirect(url_for('visitSearch', id=clientId))

#Delete a member
@app.route('/delete_member/<string:id>', methods=['POST'])
@is_logged_in
def delete_member(id):

	with sql.connect('test10.db') as connection:
		# Create cursor
		cur = connection.cursor()

		# Deletes member

		cur.execute("DELETE FROM members WHERE clientId = ?", [id])

		#deletes visits associated with member
		cur.execute("DELETE FROM visits WHERE clientId = ?", [id])

		flash('Member Deleted', 'success')

		return redirect(url_for('memberSearch'))


#Search bar for member page
@app.route('/searchBar', methods=['GET', 'POST'])
def searchBar():
	if request.method == "POST":
		# Create cursor
		cur = connection.cursor()

		# Execute
		cur.execute("SELECT * FROM members where name = %s", (search,))

		# Commit to DB
		connection.commit()

		members = cur.fetchall()

		return render_template('memberSearch.html', members=members)

	return render_template('memberSearch.html')

	#Close connection
	cur.close()

if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
