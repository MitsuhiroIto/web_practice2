from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from datetime import datetime
from werkzeug import secure_filename
import os
import boto3

app = Flask(__name__)
bucket_name = 'mitsu-web-app2'

boto3_resource_s3 = boto3.resource('s3')
boto3_client_s3 = boto3.client('s3')
boto3_client_batch = boto3.client('batch')

JOB_QUEUE = 'mitsu-batch-que'
JOB_DEFINITION = 'mitsu-batch-test'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        upload_file = request.files['upload_file']
        upload_file_name = secure_filename(upload_file.filename)
        _upload_s3_file_url = 'static/uploads/' + upload_file_name
        boto3_resource_s3.Bucket(bucket_name).upload_fileobj( upload_file, _upload_s3_file_url)
        upload_s3_file_url = boto3_client_s3.generate_presigned_url(ClientMethod='get_object',
        Params={'Bucket': bucket_name,'Key':_upload_s3_file_url })
        return render_template('index.html', upload_s3_file_url = upload_s3_file_url, upload_file_name = upload_file_name)

@app.route('/augmentation', methods=['GET', 'POST'])
def augmentation():
    if request.form['button_name'] == "Canny":
        file_name = request.form['file_name']
        file_name_af = file_name.rsplit('.', 1)[0]   + "_canny." + file_name.rsplit('.', 1)[1]
        s3_url_src = 's3://mitsu-web-app2/static/uploads/' + file_name
        s3_url_dst = 's3://mitsu-web-app2/static/uploads/' + file_name_af

        boto3_client_batch.submit_job(
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
