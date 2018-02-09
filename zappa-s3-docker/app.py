from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import boto3

app = Flask(__name__)
bucket_name = 'mitsu-zappa-s3-docker'
app.config['USE_S3_DEBUG'] = True

resource_s3 = boto3.resource('s3')
client_s3 = boto3.client('s3')
client_batch = boto3.client('batch')

JOB_QUEUE = 'mitsu-batch-que'
JOB_DEFINITION = 'mitsu-batch-test'
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
    if request.form['button_name'] == "Canny":
        file_name = request.form['upload_url'].rsplit('/', 1)[-1]
        file_name_af = file_name.rsplit('.', 1)[0]   + "_canny." + file_name.rsplit('.', 1)[1]
        s3_url_src = 's3://' + bucket_name + '/' + upload_folder + file_name
        s3_url_dst = 's3://' + bucket_name + '/' + upload_folder + file_name_af

        client_batch.submit_job(
            jobName='job-mitsu-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
            jobQueue=JOB_QUEUE,
            jobDefinition=JOB_DEFINITION,
            containerOverrides={
                    'command': [
                         "sh",
                         "shell_script/batch_test/fetch_and_run.sh"
                    ],
                    'environment': [
                        {
                        'name': 'FILE_NAME_AF',
                        'value': file_name_af
                        },
                        {
                        'name': 'BATCH_FILE_S3_URL_SRC',
                        'value': s3_url_src
                        },
                        {
                        'name': 'BATCH_FILE_S3_URL_DST',
                        'value': s3_url_dst
                        },
                    ]
                },
            )

        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
