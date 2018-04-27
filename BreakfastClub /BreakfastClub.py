from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'BreakfastClubApp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MYSQL
mysql = MySQL(app)

#Articles = Articles()

#Index
@app.route('/')
def index():
	return render_template('home.html')

#Index
@app.route('/help')
def help():
	return render_template('help.html')

#Articles
@app.route('/articles')
def articles():
		#Create cursor
		cur = mysql.connection.cursor()

		#Get Articles
		result = cur.execute("SELECT * FROM articles")

		articles = cur.fetchall()

		if result > 0:
			return render_template('articles.html', articles=articles)
		else:
			msg = 'No Articles Found'
			return render_template('articles.html', msg=msg)
		#close connection
		cur.close()

#Single Article
@app.route('/article/<string:id>/')
def article(id):
	#Create cursor
	cur = mysql.connection.cursor()

	#Get Article
	result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = cur.fetchone()
	return render_template('article.html', article=article)

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

		# Create cursor
		cur = mysql.connection.cursor()

		#execute query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		#Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('You are now registered and can now log in', 'success')

		redirect(url_for('index'))
	return render_template('register.html', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# Get form fields
		username = request.form['username']
		password_candidate = request.form['password']
		#name = request.form['name']

		#Create cursor
		cur = mysql.connection.cursor()

		#Get user by Username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			#Get stored hash
			data = cur.fetchone()
			password = data['password']

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
			cur.close()
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
	#Create cursor
	cur = mysql.connection.cursor()

#	cur.execute("UPDATE members SET totalBreakfast=(SELECT COUNT(*) FROM visits Where members.clientId = visits.clientId) ")
	#Get members
	result = cur.execute("SELECT * FROM members ORDER BY name")




#
# ******
# 	breakyCount = cur.execute("UPDATE COUNT(leftTillFree) FROM members Where")
#
# 	if statement needs to be made that "if members.LeftTillFree = 0, then show (redeem button) and reset LeftTillFree to 10)
#   a seprate table will need to be created to keep track of redeemable breakfasts'
# ********





	members = cur.fetchall()

	if result > 0:

		return render_template('memberSearch.html', members=members)
	else:
		msg = 'No members Found'
		return render_template('memberSearch.html', msg=msg)
	#close connection
	cur.close()


#Member Form class
class MemberForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])

#visitSearch (Dashboard)
@app.route('/visitSearch/<string:id>/', methods=['GET', 'POST'])
@is_logged_in
def visitSearch(id):
	#Create cursor
	cur = mysql.connection.cursor()

	#Get members

	visitResult = cur.execute("SELECT * FROM visits WHERE clientId = %s", [id])

	result = cur.execute("SELECT * from members, visits WHERE members.clientId = %s AND visits.clientId = members.clientId", [id])

 	visits = cur.fetchall()

	if result > 0:
		return render_template('visitSearch.html', visits=visits, name = visits[0]['name'])
	else:
		msg = 'No visits Found'
		return render_template('visitSearch.html', msg=msg)
	#close connection
	cur.close()

# Add Visit
@app.route('/add_visit/<string:id>/<string:name>/', methods=['GET', 'POST'])
@is_logged_in
def add_visit(id, name):
	if request.method == 'POST':

		# Create Cursor
		cur = mysql.connection.cursor()

		clientId = [id]
		name = [name]
		author = session['username']


		# Execute
		cur.execute("INSERT INTO visits(clientId,name,author) VALUES(%s,%s,%s)", (clientId,name,author))

		cur.execute("SELECT * FROM visits WHERE clientId = %s", [id])

		#cur.execute("UPDATE members SET lastBreakfastDate = now() WHERE clientId = %s", [id])

		#cur.execute("UPDATE members SET leftTillFree =leftTillFree-1 WHERE clientId = %s", [id])

		#totalBreakfast = cur.execute("UPDATE members SET totalBreakfast = (COUNT(*) from visits WHERE clientId = %s", (clientId)))

		# Commit to DB"INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('Visit created', 'success')

	return redirect(url_for('memberSearch'))

# Add member
@app.route('/add_member', methods=['GET', 'POST'])
@is_logged_in
def add_member():
	form = MemberForm(request.form)
	if request.method == 'POST' and form.validate():


		name = form.name.data
		# Create Cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("INSERT INTO members(name) VALUES(%s)",[name])

		# Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('Member Created', 'success')

		return redirect(url_for('memberSearch'))

	return render_template('add_member.html', form=form)

# Delete Visit
@app.route('/delete_visit/<string:visitId>/<string:clientId>', methods=['POST'])
@is_logged_in
def delete_visit(visitId,clientId):

	# Create cursor
	cur = mysql.connection.cursor()

	visitId = [visitId]

	# Execute Delete
	cur.execute("DELETE FROM visits WHERE visitId = %s", [visitId])

	#cur.execute("UPDATE members SET leftTillFree =leftTillFree+1 WHERE clientId = %s", [clientId])
	# Commit to DB
	mysql.connection.commit()

	#Close connection
	cur.close()

	return redirect(url_for('visitSearch', id=clientId))

#Delete a member
@app.route('/delete_member/<string:id>', methods=['POST'])
@is_logged_in
def delete_member(id):

	# Create cursor
	cur = mysql.connection.cursor()

	# Deletes member

	cur.execute("DELETE FROM members WHERE clientId = %s", [id])

	#deletes visits associated with member
	cur.execute("DELETE FROM visits WHERE clientId = %s", [id])

	# Commit to DB
	mysql.connection.commit()

	#Close connection
	cur.close()

	flash('Member Deleted', 'success')

	return redirect(url_for('memberSearch'))


#Search bar for member page
@app.route('/searchBar', methods=['GET', 'POST'])
def searchBar():
	if request.method == "POST":
		# Create cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("SELECT * FROM members where name = %s", (search,))

		# Commit to DB
		mysql.connection.commit()

		members = cur.fetchall()

		return render_template('memberSearch.html', members=members)

	return render_template('memberSearch.html')

	#Close connection
	cur.close()



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
