import pandas as pd   
from flask import Flask, render_template, request, session
from flask import send_file

app = Flask(__name__)   
app.secret_key = 'bigbootybaby'

@app.route('/') 
def upload_file():     
    return render_template('upload.html')   

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
    merged_df.to_excel(merged_filename, index=False, engine='openpyxl')  # Specify the engine for writing Excel files

    session['headers'] = list(headers_set)
    session['filename'] = merged_filename
    
    return render_template('upload.html', headers=list(headers_set), filename=merged_filename) 
          
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':     
    app.run(debug=True)
