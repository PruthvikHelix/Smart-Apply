from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from LinkedIn import apply_job
import threading
from werkzeug.utils import secure_filename
import os
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'smart_apply'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Database Connectivity
def create_database_and_table():
	conn = mysql.connector.connect(
		host = "localhost", 
		user = "root",
		password = "",
		#database = "easy_apply"
		)
	try:
		cursor = conn.cursor()
		cursor.execute("CREATE DATABASE IF NOT EXISTS easy_apply")
		conn.database = "easy_apply"
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS users (
				id INT AUTO_INCREMENT PRIMARY KEY, 
				username VARCHAR(255) UNIQUE NOT NULL,
				password VARCHAR(255) NOT NULL
				)
			"""

			)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS linkedin_credentials (
				id INT AUTO_INCREMENT PRIMARY KEY,
				user_id INT,
				email VARCHAR(255) NOT NULL,
				password VARCHAR(255) NOT NULL,
				FOREIGN KEY (user_id) REFERENCES users(id))
			""")

		cursor.execute("""
			CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(255) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id))
			""")
		cursor.execute("""
    		CREATE TABLE IF NOT EXISTS experiences (
        		user_id INT PRIMARY KEY,
        		total_experiences INT NOT NULL,
        		FOREIGN KEY (user_id) REFERENCES users(id))
			""")

		cursor.execute("""
			CREATE TABLE IF NOT EXISTS job_questions (
				id INT AUTO_INCREMENT PRIMARY KEY,
				user_id INT,
				question_text TEXT,
				option_text TEXT,
				FOREIGN KEY (user_id) REFERENCES users(id))
			""")
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS admin_questions (
				id INT AUTO_INCREMENT PRIMARY KEY,
    			question_text TEXT,
    			options TEXT)
			""")
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS user_answers (
				id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                question_id INT,
                question_text TEXT,
                options TEXT,
                answer TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (question_id) REFERENCES admin_questions(id))
        	""")


	except mysql.connector.Error as err:
		print("Error: {}".format(err))
	finally:
		if cursor in locals():
			cursor.close()
		conn.close()

#call function to create database and table
create_database_and_table()

#Database connection
conn = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "",
	database = "easy_apply"
	)
@app.route('/')
def home():
	return render_template('login.html', message="")
"""
# Fetch admin questions
def get_admin_questions():
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_text FROM admin_questions")
    questions = cursor.fetchall()
    cursor.close()
    return questions
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		cursor = conn.cursor()
		cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
		user = cursor.fetchone()

		if user:
			session['username'] = user[1]
			cursor.close()
			return redirect('/dashboard')
		else:
			cursor.close()
			return render_template('login.html', message="Invalid username or password")
	return render_template('login.html', message="")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		cursor = conn.cursor()
		try:
			cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
			conn.commit()
			cursor.close()
			return redirect('/login')
		except mysql.connector.Error as err:
			cursor.close()
			return render_template('signup.html', message="Username Already exist please choose other one")
	return render_template('signup.html', message="")

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	if 'username' in session:
		if request.method == 'POST':
			linkedin_email = request.form['linkedin_email']
			linkedin_password = request.form['linkedin_password']

			cursor = conn.cursor()
			cursor.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
			user_id = cursor.fetchone()[0]

			cursor.execute("SELECT id FROM linkedin_credentials WHERE user_id=%s", (user_id,))
			result = cursor.fetchone()

			if result:
				cursor.execute("UPDATE linkedin_credentials SET email=%s, password=%s WHERE user_id=%s", (linkedin_email, linkedin_password,user_id))
			else:
				cursor.execute("INSERT INTO linkedin_credentials (user_id, email, password) VALUES (%s, %s, %s)", (user_id, linkedin_email, linkedin_password))

			conn.commit()
			cursor.close()
		#Fetching and passing LinkedIn credentials to the template
		cursor = conn.cursor()
		cursor.execute("SELECT email, password FROM linkedin_credentials WHERE user_id=(SELECT id FROM users Where username=%s)", (session['username'],))
		linkedin_credentials = cursor.fetchone()
		cursor.close()

		# Fetching unanswered questions
		cursor = conn.cursor()
		cursor.execute("""
			SELECT id, question_text, options
			FROM admin_questions
			WHERE id NOT IN (SELECT question_id FROM user_answers WHERE user_id=(SELECT id FROM users WHERE username=%s))
			""", (session['username'],))
		admin_questions = cursor.fetchall()
		cursor.close()

		#fetching to display experience in template
		cursor = conn.cursor()
		cursor.execute("SELECT total_experiences FROM experiences WHERE user_id=(SELECT id FROM users WHERE username=%s)", (session['username'],))
		total_experiences = cursor.fetchone()
		#print("Total experiences:", total_experiences)
		#cursor.fetchall()
		cursor.close()

		if total_experiences:
			print("Total Experiences:", total_experiences[0])

		return render_template('dashboard.html', username=session['username'], linkedin_credentials=linkedin_credentials,total_experiences=total_experiences, admin_questions=admin_questions)
		#return f"Welcome, {session['username']}!"
	else:
		return redirect('/')
@app.route('/set_total_experiences', methods=['POST'])
def set_total_experiences():
    if 'username' in session:
        if request.method == 'POST':
            total_experiences = request.form['total_experiences']
            if total_experiences.isdigit():  # Validate input
                total_experiences = int(total_experiences)
                cursor = conn.cursor()
                # Query user_id based on username
                cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
                user_id = cursor.fetchone()
                if user_id:
                    user_id = user_id[0]
                    # Check if a record already exists for the user
                    cursor.execute("SELECT user_id FROM experiences WHERE user_id = %s", (user_id,))
                    existing_row = cursor.fetchone()
                    if existing_row:
                        cursor.execute("UPDATE experiences SET total_experiences = %s WHERE user_id = %s", (total_experiences, user_id))
                    else:
                        cursor.execute("INSERT INTO experiences (user_id, total_experiences) VALUES (%s, %s)", (user_id, total_experiences))
                    conn.commit()
                    cursor.close()
                    flash('Total experiences set successfully')
                else:
                    flash('User does not exist')
            else:
                flash('Invalid input for total experiences. Please enter a number.')
            return redirect('/dashboard')
    else:
        return redirect('/')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('username', None)
        return redirect('/')
    else:
        # Handle GET request if needed
        return redirect('/')

def apply_job_async(conn, email, password, job, location, resume_filepath, total_experiences, user_id):
    thread = threading.Thread(target=apply_job, args=(conn, email, password, job, location, resume_filepath, total_experiences, user_id))
    thread.start()

@app.route('/apply_job', methods=['POST'])
def trigger_apply_job():
	if request.method == 'POST':
		
		cursor = conn.cursor()
		cursor.execute("SELECT email, password FROM linkedin_credentials WHERE user_id=(SELECT id FROM users WHERE username=%s)", (session['username'],))
		credentials = cursor.fetchone()
		if credentials:
			email, password = credentials
			job = request.form['job']
			location = request.form['location']

			cursor.execute("SELECT total_experiences FROM experiences WHERE user_id=(SELECT id FROM users WHERE username=%s)", (session['username'],))
			total_experiences_row = cursor.fetchone()
			total_experiences = total_experiences_row[0] if total_experiences_row else None
			#if total_experiences:
			#	total_experiences = total_experiences[0]

			cursor.execute("SELECT filepath FROM resumes WHERE user_id=(SELECT id FROM users WHERE username=%s)", (session['username'],))
			resume_row = cursor.fetchone()
			resume_filepath = resume_row[0] if resume_row else None
			#print("Resume Filepath:", resume_filepath)

			cursor.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
			user_id = cursor.fetchone()[0]

			cursor.close()

			apply_job_async(conn, email, password, job, location, resume_filepath, total_experiences, user_id)
			return redirect('/dashboard')
		else:
			cursor.close()
			return redirect('/dashboard')
		#apply_job()
		#return redirect('/dashboard')
	else:
		return redirect('/')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'username' in session:
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            absolute_filepath = os.path.abspath(filepath)  # Convert to absolute path
            file.save(filepath)
            
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
            user_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO resumes (user_id, filename, filepath) VALUES (%s, %s, %s)", (user_id, filename, absolute_filepath))
            conn.commit()
            cursor.close()
            
            flash('Resume uploaded successfully')
            return redirect('/dashboard')
        
        else:
            flash('Invalid file format. Please upload PDF or Word document')
            return redirect(request.url)
    
    else:
        return redirect('/')
@app.route('/add_question', methods=['GET','POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form['question_text']
        options = request.form.getlist('options') #get list of options

        options_str = ','.join(options)        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admin_questions (question_text, options) VALUES (%s, %s)", (question_text,options_str))
        conn.commit()
        cursor.close()
        
        return redirect('/add_question')
    else:
    	return render_template('admin_interface.html')

@app.route('/get_question_options', methods=['GET'])
def get_question_options():
    question_id = request.args.get('id')  # Get the question ID from the query parameters
    # Fetch options for the selected question from the database
    cursor = conn.cursor()
    cursor.execute("SELECT options FROM admin_questions WHERE id = %s", (question_id,))
    options = cursor.fetchone()
    cursor.close()
    
    if options:
        options_list = options[0].split(',')  # Assuming options are stored as a comma-separated string in the database
        return jsonify(options=options_list)
    else:
        return jsonify(options=[])  # Return an empty list if no options found
@app.route('/save_answer', methods=['POST'])
def save_answer():
    if 'username' in session:
        if request.method == 'POST':
            data = request.json
            question_id = data.get('question_id')
            selected_option = data.get('selected_option')

            cursor = conn.cursor()
            # Fetch user_id based on username
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user_id = cursor.fetchone()[0]

            # Fetch question text and options based on question_id
            cursor.execute("SELECT question_text, options FROM admin_questions WHERE id = %s", (question_id,))
            question_data = cursor.fetchone()
            if question_data:
                question_text = question_data[0]
                options = question_data[1]

                # Store the question, options, and selected option in the user_answers table
                cursor.execute("INSERT INTO user_answers (user_id, question_id, question_text, options, answer) VALUES (%s, %s, %s, %s, %s)",
                               (user_id, question_id, question_text, options, selected_option))
                conn.commit()
                cursor.close()

                #session.setdefault('answered_questions', []).append(question_id)

                return jsonify(success=True)
    return jsonify(success=False)


if __name__ == '__main__':
	app.run(debug = True)