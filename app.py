from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from datetime import datetime
from werkzeug import secure_filename
import os
import boto3

app = Flask(__name__)
bucket_name = 'mitsu-web-app2'
app.config['FLASKS3_BUCKET_NAME'] = bucket_name
app.config['USE_S3_DEBUG'] = True

boto3_resource = boto3.resource('s3')
boto3_client = boto3.client('s3')

############### 初めのページ#############################
@app.route('/')
def index():
    profile_name_url = boto3_client.generate_presigned_url(ClientMethod='get_object',
    Params={'Bucket': bucket_name,'Key': 'static/img/profile.jpg'})
    return render_template('index.html', profile_name_url = profile_name_url)

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        upload_file = request.files['upload_file']
        upload_file_name = secure_filename(upload_file.filename)
        upload_s3_file_url = 'static/uploads/' + upload_file_name
        boto3_resource.Bucket(app.config['FLASKS3_BUCKET_NAME']).upload_fileobj( upload_file, upload_s3_file_url)
        upload_s3_file_url = profile_name_url = boto3_client.generate_presigned_url(ClientMethod='get_object',
        Params={'Bucket': bucket_name,'Key':upload_s3_file_url })
        profile_name_url = boto3_client.generate_presigned_url(ClientMethod='get_object',
        Params={'Bucket': bucket_name,'Key': 'static/img/profile.jpg'})
        return render_template('index.html', upload_s3_file_url = upload_s3_file_url, profile_name_url = profile_name_url)

if __name__ == "__main__":
    app.debug = True
    app.run()
