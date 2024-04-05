from flask import Flask, render_template, request
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile
import os
from flask import session

app = Flask(__name__)
app.secret_key = 'fuckingpussy'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
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
    # Get the selected headers from the form data
    selected_headers = request.form.get('selected_headers').split(',')
    selected_headers = [header.strip() for header in selected_headers]

    # Remove "Selected Headers:" and "Merge Data" from the selected headers
    unwanted_headers = ['Selected Headers:', 'Merge Data']
    selected_headers = [header for header in selected_headers if header not in unwanted_headers]

    print('Selected headers:', selected_headers)

    # Read the uploaded files from the paths stored in the session
    try:
        file1_df = pd.read_excel(session['file1_path'])
        file2_df = pd.read_excel(session['file2_path'])
    except Exception as e:
        return 'Error: Failed to read uploaded files: ' + str(e)

    print('File 1 headers:', file1_df.columns.tolist())
    print('File 2 headers:', file2_df.columns.tolist())

    # Check if the selected headers exist in the dataframes
    if not set(selected_headers).issubset(file1_df.columns) or not set(selected_headers).issubset(file2_df.columns):
        return 'Error: One or more selected headers do not exist in the data'

    merged_data = pd.concat([file1_df[selected_headers], file2_df[selected_headers]], ignore_index=True)

    return merged_data.to_html()

if __name__ == '__main__':
    app.run(debug=True)
