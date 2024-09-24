import os
import MySQLdb
from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.utils import secure_filename
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Set the upload folder and allowed file types
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configure the app to use the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection setup
db = MySQLdb.connect(
    host='localhost',
    user='root',  # Replace with your MySQL username
    passwd='',    # Replace with your MySQL password
    db='education_institution'
)

cursor = db.cursor()

# List of courses
COURSES = [
    "Web Development",
    "Data Science",
    "Mobile App Development",
    "Cyber Security",
    "AI & Machine Learning",
    "Internet of Things (IoT)",
    "Software Testing",
    "UI/UX Design"
]

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Index route
@app.route('/')
def index():
    return render_template('index.html')

# Login route
from datetime import datetime

# Login route
from datetime import datetime

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query to get user details
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            # Ensure dob is a date object
            dob = user[5]
            if isinstance(dob, str):
                try:
                    # Convert string to datetime object
                    dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    dob = None  # Handle cases where the date format is incorrect

            # Store user details in session
            session['user'] = {
                'name': user[1],
                'address': user[4],
                'age': user[3],
                'dob': dob,  # Now it's either a date or None
                'username': user[6],
                'profile_photo': user[8],  # Assuming the 8th column is profile_photo
                'course': user[9]           # Assuming the 9th column is course
            }
            return redirect(url_for('display'))  # Redirect to display page
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        dob = request.form['dob']
        age = request.form['age']
        username = request.form['username']
        password = request.form['password']
        course = request.form['course']  # Get selected course

        # Handle file upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_photo_path = filename  # Store just the filename for the database
            else:
                return "Invalid file type."
        else:
            profile_photo_path = None  # Handle case where no file is uploaded

        cursor.execute("INSERT INTO users (name, address, age, dob, username, password, course, profile_photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (name, address, age, dob, username, password, course, profile_photo_path))
        db.commit()

        return redirect(url_for('login'))
    return render_template('register.html', courses=COURSES)  # Pass courses to the template

# Display user information after login
@app.route('/display')
def display():
    if 'user' in session:
        user = session['user']
        return render_template('display.html', user=user)
    else:
        return redirect(url_for('login'))  # Redirect to login if no user is logged in

# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)

# Clean up database connection on exit
@app.teardown_appcontext
def close_db(error):
    if cursor:
        cursor.close()
    if db:
        db.close()
