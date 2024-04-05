import pandas as pd   
from flask import Flask, render_template, request, session, send_file
import os
from flask import url_for
from flask import redirect

app = Flask(__name__)   
app.secret_key = 'bigbootybaby'
"""
@app.route('/') 
def upload_file():     
    return render_template('upload.html')   
"""
@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Hardcoded credentials for testing
    if username == 'user1' and password == 'wordpass':
        session['username'] = username  # Store username in session
        return redirect(url_for('upload_file'))  # Redirect to upload page
    else:
        return render_template('landing.html', error='Invalid username or password')  # Display error message

@app.route('/upload')
def upload_file():
    if 'username' not in session:
        return redirect(url_for('landing_page'))  # Redirect to landing page if not logged in
    return render_template('upload.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing_page'))



@app.route('/merge', methods=['POST']) 
def merge_files():     
    files = request.files.getlist('files[]') 
    filename = request.form['filename']      

    if len(files) < 2:         
        return "Please upload at least 2 files for merging."  

    dfs = []     
    headers_set = None    
    for file in files:         
        df = pd.read_excel(file, engine='openpyxl')  # Specify the engine for reading Excel files         
        if headers_set is None:             
            headers_set = set(df.columns)         
        else:             
            headers_set &= set(df.columns)  # Intersection of column headers         
        dfs.append(df)       

    if len(headers_set) == 0:         
        return "No common column headers found for merging."       

    session['headers'] = list(headers_set)
    session['dfs'] = dfs  # Store the dataframes in session
    session['filename'] = filename if filename else 'merged_file'  # Store the filename in session

    return redirect(url_for('select_columns'))  # Redirect to column selection page




@app.route('/select_columns', methods=['GET', 'POST'])
def select_columns():
    if 'username' not in session:
        return redirect(url_for('landing_page'))  # Redirect to landing page if not logged in

    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')  # Get the selected columns
        dfs = session['dfs']
        merged_df = pd.concat(dfs, ignore_index=True)  
        merged_df = merged_df[selected_columns]  # Filter columns based on the selected headers
        merged_filename = session['filename']
        merged_df.to_excel(merged_filename + '.xlsx', index=False, engine='openpyxl')
        session['merged_filename'] = merged_filename + '.xlsx'
        return redirect(url_for('download_file'))  # Redirect to download page
    else:
        headers = session['headers']
        return render_template('select_columns.html', headers=headers)  # Display the common columns for selection


@app.route('/download_merged_file')
def download_merged_file():
    if 'username' not in session:
        return redirect(url_for('landing_page'))  # Redirect to landing page if not logged in

    filename = session['merged_filename']
    return send_file(filename, as_attachment=True)  # Provide the file for download

@app.route('/download/<filename>', methods=['GET'])
def download_specific_file(filename):
    # Ensure the downloaded file has the correct extension
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    # Get the full file path
    file_path = os.path.abspath(filename)
    
    return send_file(file_path, as_attachment=True)
if __name__ == '__main__':     
    app.run(debug=True)