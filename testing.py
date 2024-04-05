from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file1 = pd.read_excel(request.files['file1'])
    file2 = pd.read_excel(request.files['file2'])

    file1_headers = file1.columns
    file2_headers = file2.columns

    common_headers = list(set(file1_headers).intersection(file2_headers))

    return render_template('index.html', common_headers=common_headers)

if __name__ == '__main__':
    app.run(debug=True)
