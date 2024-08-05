from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile
import os
from flask import send_file
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')  # Use the secret key from .env
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()

merged_data = None

@app.route('/')
def landing():
    return render_template('newlanding.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists!'
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials, please try again.'
    return render_template('login.html')

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('landing'))
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('landing'))

    # Get the list of uploaded files
    files = request.files.getlist('file')

    if len(files) != 2:
        return 'Error: You must upload exactly two files'

    # Save the uploaded files to a temporary directory
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    for file in files:
        file_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(file_path)
        file_paths.append(file_path)

    # Store the paths to the uploaded files in the session
    session['file_paths'] = file_paths

    # Read the uploaded files
    try:
        dfs = [pd.read_excel(file_path) for file_path in file_paths]
    except Exception as e:
        return 'Error: Failed to read uploaded files: ' + str(e)

    common_headers = list(set(dfs[0].columns).intersection(dfs[1].columns))

    return render_template('index.html', common_headers=common_headers)

@app.route('/merge', methods=['POST'])
def merge():
    if not session.get('logged_in'):
        return redirect(url_for('landing'))

    global merged_data

    # Get the selected headers from the form data
    selected_headers = request.form.get('selected_headers').split(',')
    selected_headers = [header.strip() for header in selected_headers]

    # Remove "Selected Headers:" and "Merge Data" from the selected headers
    unwanted_headers = ['Selected Headers:', 'Merge Data']
    selected_headers = [header for header in selected_headers if header not in unwanted_headers]

    # Read the uploaded files from the paths stored in the session
    try:
        dfs = [pd.read_excel(file_path) for file_path in session['file_paths']]
    except Exception as e:
        return 'Error: Failed to read uploaded files: ' + str(e)

    # Check if the selected headers exist in the dataframes
    if not all(set(selected_headers).issubset(df.columns) for df in dfs):
        return 'Error: One or more selected headers do not exist in the data'

    merged_data = pd.concat([df[selected_headers] for df in dfs], ignore_index=True)

    # Convert the DataFrame to HTML and return it
    merged_data_html = merged_data.to_html()

    return render_template('index.html', merged_data_html=merged_data_html)

@app.route('/download', methods=['GET'])
def download():
    if not session.get('logged_in'):
        return redirect(url_for('landing'))

    global merged_data
    if merged_data is None:
        return "No data to download"

    # Write the DataFrame to an Excel file
    merged_data.to_excel('merged_data.xlsx', index=False)

    # Send the file to the user
    return send_file('merged_data.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
