from flask import Flask, render_template, request, redirect, send_file 
import pandas as pd   

app = Flask(__name__)   

# HTML form to upload files 
@app.route('/') 
def upload_file():     
    return render_template('upload.html')   

# Merge uploaded files 
@app.route('/merge', methods=['POST']) 
def merge_files():     
    files = request.files.getlist('files[]')       
    
    if len(files) < 2:         
        return "Please upload at least 2 files for merging."       
    
    dfs = []     
    headers_set = None    
    for file in files:         
        df = pd.read_excel(file)         
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
        
        merged_filename = 'merged_file.xlsx'     
        merged_df.to_excel(merged_filename, index=False)       
        
        return send_file(merged_filename, as_attachment=True)
       
    if __name__ == '__main__':     
        app.run(debug=True)