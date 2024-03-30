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
        
    merged_df = pd.concat(dfs, ignore_index=True)      
    # Filter columns based on the common headers     
    merged_df = merged_df[[col for col in merged_df.columns if col in headers_set]]       

    merged_filename = filename if filename else 'merged_file.xlsx'     
    merged_df.to_excel(merged_filename + '.xlsx', index=False, engine='openpyxl')

    if not filename.endswith('.xlsx'):  # Ensure the filename has the correct extension
        filename += '.xlsx'

    session['headers'] = list(headers_set)
    session['filename'] = merged_filename
    
    return render_template('upload.html', headers=list(headers_set), filename=merged_filename) 
          
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Ensure the downloaded file has the correct extension
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    # Get the full file path
    file_path = os.path.abspath(filename)
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':     
    app.run(debug=True)
