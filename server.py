
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import random
import datetime
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "yl5444"
DATABASE_PASSWRD = "yl5444"
DATABASE_HOST = "35.212.75.104" # change to 34.148.107.47 | 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)
cur_user = None


#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/', methods=["GET", "POST"])
def login():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""
	
	# DEBUG: this is debugging code to see what request looks like
	# print(request.args)


	#
	# example of a database query
	#
	# select_query = "SELECT name from test"
	# cursor = g.conn.execute(text(select_query))
	# names = []
	# for result in cursor:
	# 	names.append(result[0])
	# cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	# context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	# val = g.conn.execute("SELECT email_address FROM users where email_address = %s", email)
	# print(val)

	return render_template("login.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/signup', methods=['POST', 'GET'])
def signup():

	if request.method =='POST':
		email = request.form.get('email')
		params = {}
		params['new_email'] = email

		val = g.conn.execute(text('SELECT email_address FROM users where email_address = (:new_email)'), params)

		if val.rowcount > 0:
			global cur_user
			result = g.conn.execute(text("SELECT user_id FROM users where email_address = (:new_email)"), params)
			for i in result:
				cur_user = i[0]
			return redirect('/recommend')
		else:
			return redirect('/notfound')
	
	return render_template("signup.html")
@app.route('/notfound')
def notfound():
	return render_template('notfound.html')

# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
# 	# accessing form inputs from user
# 	name = request.form['name']
	
# 	# passing params in for each variable into query
# 	params = {}
# 	params["new_name"] = name
# 	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
# 	g.conn.commit()
# 	return redirect('/')


@app.route('/recommend', methods=['POST', 'GET'])
def recommend():
	global cur_user
	cursor = g.conn
	
	if request.method == 'POST':
		email_address = request.form['email_address']
		address = request.form['address']
		city = request.form['city']
		zip = request.form['zip']
		country = request.form['country']
		dob = request.form['dob']
		height = request.form['height']
		weight = request.form['weight']

		params = {}
		params['new_community_id'] = None
		params['new_email_address'] = email_address
		params["new_address"] = address
		params["new_city"] = city
		params["new_zip"] = zip
		params["new_country"] = country
		params["new_dob"] = dob
		params["new_height"] = height
		params["new_weight"] = weight
		params['today'] = datetime.date.today()
		params['guest'] = False
		
		cursor.execute(text('INSERT INTO users(email_address, join_date, street_address, city, zip, country, is_guest, dob) VALUES (:new_email_address, :today, :new_address, :new_city, :new_zip, :new_country, :guest, :new_dob)'), params)
		cursor.execute(text('INSERT INTO biometrics(height, weight) VALUES (:new_height, :new_weight)'), params)
		cursor.commit()

		result = cursor.execute(text('SELECT user_id from users where email_address = (:new_email_address)'), params)
		for i in result:
			cur_user = i[0]

	if not cur_user:
		return redirect('/guestrecommend')

	params = {}
	params['new_cur_user'] = cur_user
	params['easy'] = '1'
	params['medium'] = '2'
	params['hard'] = '3'

	bio = cursor.execute(text('SELECT height, weight FROM biometrics where user_id = (:new_cur_user)'), params)
	height = 0
	weight = 0
	for i in bio:
		height = i[0]/100
		weight = i[1]
	bmi = weight/(height**2)
	print(bmi)
	

	if bmi < 18.5 or bmi > 25:
		ideal = list(cursor.execute(text('SELECT * FROM routine where routine_id = (:easy)'), params))[0]
		routine_id = '1'
	elif bmi > 20:
		ideal = list(cursor.execute(text('SELECT * FROM routine where routine_id = (:medium)'), params))[0]
		routine_id = '2'
	else:
		ideal = list(cursor.execute(text('SELECT * FROM routine where routine_id = (:hard)'), params))[0]
		routine_id = '3'

	rest = 0

	for ind, fragment in enumerate(ideal):
		if ind == len(list(ideal)) - 1:
			rest = fragment
			break
		id = str(fragment[0])
		params[str(ind + 1)] = id



	header_arr = ["", "Half Crimp", "Full Crimp", "Dead Hang", "Three Finger Drag", "Sloper Hang"]

	data_arr = [['' for j in range(6)] for i in range(3)]
	data_arr[0][0] = 'Weight'
	data_arr[1][0] = "Height"
	data_arr[2][0] = "Edge/Angle"

	it_arr = []
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM half_crimp where half_crimp_id = (:1)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM full_crimp where full_crimp_id = (:2)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM dead_hang where dead_hang_id = (:3)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM three_finger where three_finger_id = (:4)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, angle FROM sloper_hang where sloper_hang_id = (:5)'), params))[0])

	for  ind, it in enumerate(it_arr):
		for ind_t, t in enumerate(it):
			data_arr[ind_t][ind + 1] = t

	

	return render_template('recommend.html', data_arr = data_arr, header_arr=header_arr, rest=rest, routine_id =routine_id)

@app.route('/complete', methods=['POST', 'GET'])
def complete():
	r_id = request.form['r_id']

	return render_template('/complete.html', routine_id=r_id)

@app.route('/guestrecommend', methods=['POST', 'GET'])
def guestrecommend():
	cursor = g.conn
	params = {}
	params['easy'] = '1'
	ideal = list(cursor.execute(text('SELECT * FROM routine where routine_id = (:easy)'), params))[0]
	rest = 0

	for ind, fragment in enumerate(ideal):
		if ind == len(list(ideal)) - 1:
			rest = fragment
			break
		id = str(fragment[0])
		params[str(ind + 1)] = id



	header_arr = ["", "Half Crimp", "Full Crimp", "Dead Hang", "Three Finger Drag", "Sloper Hang"]

	data_arr = [['' for j in range(6)] for i in range(3)]
	data_arr[0][0] = 'Weight'
	data_arr[1][0] = "Hang Time"
	data_arr[2][0] = "Edge/Angle"

	it_arr = []
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM half_crimp where half_crimp_id = (:1)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM full_crimp where full_crimp_id = (:2)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM dead_hang where dead_hang_id = (:3)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM three_finger where three_finger_id = (:4)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, angle FROM sloper_hang where sloper_hang_id = (:5)'), params))[0])

	for  ind, it in enumerate(it_arr):
		for ind_t, t in enumerate(it):
			data_arr[ind_t][ind + 1] = t

	return render_template('/guestrecommend.html', header_arr=header_arr, data_arr=data_arr, rest=rest)

@app.route('/customized', methods = ['POST', 'GET'])
def customized():
	cursor = g.conn
	r_id = request.form['r_id']

	params = {}
	params['r_id'] = r_id
	routine = list(cursor.execute(text('SELECT * FROM routine where routine_id = (:r_id)'), params))[0]
	rest = 0

	for ind, fragment in enumerate(routine):
		if ind == len(list(routine)) - 1:
			rest = fragment
			break
		id = str(fragment[0])
		params[str(ind + 1)] = id


	header_arr = ["", "Half Crimp", "Full Crimp", "Dead Hang", "Three Finger Drag", "Sloper Hang"]

	data_arr = [['' for j in range(6)] for i in range(3)]
	data_arr[0][0] = 'Weight'
	data_arr[1][0] = "Height"
	data_arr[2][0] = "Edge/Angle"

	it_arr = []
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM half_crimp where half_crimp_id = (:1)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM full_crimp where full_crimp_id = (:2)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM dead_hang where dead_hang_id = (:3)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, edge FROM three_finger where three_finger_id = (:4)'), params))[0])
	it_arr.append(list(cursor.execute(text('SELECT weight, time, angle FROM sloper_hang where sloper_hang_id = (:5)'), params))[0])

	for ind, it in enumerate(it_arr):
		for ind_t, t in enumerate(it):
			data_arr[ind_t][ind + 1] = t

	return render_template('recommend.html', data_arr=data_arr, header_arr=header_arr, rest=rest, routine_id = r_id)

@app.route('/finish', methods =['POST', 'GET'])
def finish():
	r_id = request.form['r_id']
	dif = int(request.form['difficulty'])
	complete = True if 'complete' in request.form else False

	cursor = g.conn 
	params = {}
	params['u_id'] = cur_user
	params['r_id'] = r_id
	params['dif'] = dif
	params['complete'] = complete

	cursor.execute(text("INSERT INTO completes (user_id, routine_id, completeness, difficulty) VALUES (:u_id, :r_id, :complete, :dif) ON CONFLICT (user_id, routine_id) DO UPDATE SET completeness = :complete, difficulty =:dif"), params)

	scale = 0

	if complete:
		if dif // 2 == 5:
			scale = 1
		else:
			scale = 5 - (dif // 2)
	else:
		if dif > 5:
			scale = 5 - dif

	cur_routine = list(cursor.execute(text('SELECT * FROM routine where routine_id = (:r_id)'), params))[0][1:]

	n_ele = random.randint(1, 5)
	decision = random.choices([i for i in range(5)], weights=[2, 3, 1, 2, 3], k=n_ele)

	for ind, id in enumerate(cur_routine):
		params[str(ind)] = str(id)

	for ind in decision:
		if int(params[str(ind)]) + scale < 1:
			params[str(ind)] = str(1)
		elif int(params[str(ind)]) + scale > 10:
			params[str(ind)] = str(10)
		else:
			params[str(ind)] = str(int(params[str(ind)]) + scale)



	cursor.execute(text('INSERT INTO routine(half_crimp_id, full_crimp_id, dead_hang_id, three_finger_id, sloper_hang_id, rest) VALUES (:0, :1, :2, :3, :4, :5) ON CONFLICT (half_crimp_id, full_crimp_id, dead_hang_id, three_finger_id, sloper_hang_id, rest) DO NOTHING'), params)

	cursor.commit()
	
	routine_id = list(cursor.execute(text('SELECT routine_id FROM routine WHERE half_crimp_id = :0 AND full_crimp_id = :1 AND dead_hang_id = :2 AND three_finger_id = :3 AND sloper_hang_id = :4 AND rest::bigint = :5'), params))[0][0]
	return render_template('finish.html', r_id=routine_id, o_r_id = r_id)

if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
