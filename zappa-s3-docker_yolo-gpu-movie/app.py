from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import boto3
import json

app = Flask(__name__)
bucket_name = 'mitsu-aws-image'
app.config['USE_S3_DEBUG'] = True

resource_s3 = boto3.resource('s3')
client_s3 = boto3.client('s3')
client_batch = boto3.client('batch')

JOB_QUEUE = 'test5_queue'
JOB_DEFINITION = 'test5_def'
upload_folder = 'static/uploads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        upload_file = request.files['upload_file']
        resource_s3.Bucket(bucket_name).put_object(Key= upload_folder + upload_file.filename, Body=upload_file.read(), ACL='public-read')
        upload_url = 'https://s3-ap-northeast-1.amazonaws.com/' + bucket_name + '/' + upload_folder + upload_file.filename
        client_s3.get_waiter('object_exists').wait(Bucket=bucket_name, Key=upload_folder + upload_file.filename)
        return render_template('index.html', upload_url = upload_url )

@app.route('/augmentation', methods=['GET', 'POST'])
def augmentation():
    if request.form['button_name'] == "YOLO":
        f = open('batch_job.json', 'r')
        containerOverrides = json.load(f)

        containerOverrides['environment'][0]['value'] = file_name = request.form['upload_url'].rsplit('/', 1)[-1]
        containerOverrides['environment'][1]['value'] = file_name_af = file_name.rsplit('.', 1)[0]   + "_yolo." + file_name.rsplit('.', 1)[1]
        containerOverrides['environment'][2]['value'] = 's3://' + bucket_name + '/' + upload_folder + file_name
        containerOverrides['environment'][3]['value'] = 's3://' + bucket_name + '/' + upload_folder + file_name_af
        containerOverrides['command']=["sh","shell_script/detect_yolo-gpu-movie/fetch_and_run.sh"]

        client_batch.submit_job(
            jobName='job-mitsu-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
            jobQueue=JOB_QUEUE,
            jobDefinition=JOB_DEFINITION,
            containerOverrides=containerOverrides
            )

        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
