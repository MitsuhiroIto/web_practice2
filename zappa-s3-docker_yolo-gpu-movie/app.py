from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import boto3
import json

app = Flask(__name__)
bucket_name = 'mitsu-aws-image'
app.config['USE_S3_DEBUG'] = True
ALLOWED_EXTENSIONS = set(['png', 'jpg','jpeg', 'avi'])
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

resource_s3 = boto3.resource('s3')
resource_sns = boto3.resource('sns')
client_s3 = boto3.client('s3')
client_batch = boto3.client('batch')
client_events = boto3.client('events')
client_sns = boto3.client('sns')

upload_folder = 'static/uploads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        upload_file = request.files['upload_file']
        if upload_file and allowed_file(upload_file.filename):
            resource_s3.Bucket(bucket_name).put_object(Key= upload_folder + upload_file.filename, Body=upload_file.read(), ACL='public-read')
            upload_url = 'https://s3-ap-northeast-1.amazonaws.com/' + bucket_name + '/' + upload_folder + upload_file.filename
            client_s3.get_waiter('object_exists').wait(Bucket=bucket_name, Key=upload_folder + upload_file.filename)
            return render_template('index.html', upload_url = upload_url )
        else:
            return render_template('index.html', warning="warning")

@app.route('/augmentation', methods=['GET', 'POST'])
def augmentation():
    if request.form['button_name'] == "YOLO":
        if not request.form['mail']:
            return render_template('index.html', warning2="warning2")
        f = open('json/batch_job.json', 'r')
        job = json.load(f)
        job['submit_job']['environment'][0]['value'] = file_name = request.form['upload_url'].rsplit('/', 1)[-1]
        job['submit_job']['environment'][1]['value'] = file_name_af = file_name.rsplit('.', 1)[0]   + "_yolo." + file_name.rsplit('.', 1)[1]
        job['submit_job']['environment'][2]['value'] = 's3://' + bucket_name + '/' + upload_folder + file_name
        job['submit_job']['environment'][3]['value'] = 's3://' + bucket_name + '/' + upload_folder + file_name_af

        if file_name.rsplit('.', 1)[1] == 'avi' or file_name.rsplit('.', 1)[1] == 'mp4':
            job['submit_job']['command']=["sh","shell_script/detect_yolo-movie/fetch_and_run.sh"]

        else :
            job['submit_job']['command']=["sh","shell_script/detect_yolo-image/fetch_and_run.sh"]

        url_download =client_s3.generate_presigned_url(
            ClientMethod = 'get_object',
            Params = {'Bucket' : bucket_name, 'Key' : upload_folder + file_name_af},
            ExpiresIn = 3600,
            HttpMethod = 'GET'
            )
        client_batch.submit_job(
            jobName='job-mitsu-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
            jobQueue=job['queue_name'],
            jobDefinition=job['definition_name'],
            containerOverrides=job['submit_job']
            )

        topic_name = 'batch'
        client_sns.create_topic(Name=topic_name)
        client_sns.subscribe(
            TopicArn=resource_sns.create_topic(Name=topic_name).arn,
            Protocol='email',
            Endpoint=request.form['mail'])
        client_sns.set_topic_attributes(
            TopicArn=resource_sns.create_topic(Name=topic_name).arn,
            AttributeName='Policy',
            AttributeValue=json.dumps({
                  "Id": "Policy1519298170820",
                  "Version": "2012-10-17",
                  "Statement": [{
                        "Sid": "TrustCWEToPublishEventsToMyTopic",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "events.amazonaws.com"
                                    },
                        "Action": "sns:Publish",
                        "Resource":resource_sns.create_topic(Name=topic_name).arn
                                }]
                        })
            )
        client_events.put_rule(
            Name=topic_name,
            State='ENABLED',
            EventPattern=json.dumps({
                  "source": ["aws.batch"],
                  "detail-type": ["Batch Job State Change"],
                  "detail": {"status": ["SUCCEEDED"]}
                  })
            )
        mail_text = "Finish your work! You can down load here. "  + url_download
        client_events.put_targets(
            Rule=topic_name,
            Targets=[{
                    "Id": 'batch',
                    "Arn": resource_sns.create_topic(Name=topic_name).arn,
                    "Input": json.dumps(mail_text)
            }]
        )

        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
