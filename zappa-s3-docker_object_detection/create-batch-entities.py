import boto3
import argparse
import time
import sys
import json

batch = boto3.client('batch')

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--compute-environment", help="name of the compute environment", type=str, required=True)
parser.add_argument("--subnets", help="comma delimited list of subnets", type=str, default='subnet-31146569')
parser.add_argument("--security-groups", help="comma delimited list of security group ids",type=str, default='sg-10dbac69')
parser.add_argument("--instance-role", help="instance role", type=str, default='arn:aws:iam::251699169519:instance-profile/ecsInstanceRole')
parser.add_argument("--service-role", help="service role", type=str, default='arn:aws:iam::251699169519:role/service-role/AWSBatchServiceRole')
parser.add_argument("--container", help="container", type=str, default='251699169519.dkr.ecr.ap-northeast-1.amazonaws.com/mitsuhiro3116/object_detection')
parser.add_argument("--image-id", help="image id", type=str, default='ami-319bde57')
parser.add_argument("--key-pair", help="ec2 key pair", type=str, default='mitsu-aws2')
args = parser.parse_args()

spin = ['-', '/', '|', '\\', '-', '/', '|', '\\']

def create_compute_environment(computeEnvironmentName, instanceType, unitVCpus, imageId, serviceRole, instanceRole,
                               subnets, securityGroups, keyPair):
    response = batch.create_compute_environment(
        computeEnvironmentName=computeEnvironmentName,
        type='MANAGED',
        serviceRole=serviceRole,
        computeResources={
            'type': 'EC2',
            'imageId': imageId,
            'minvCpus': 1,
            'maxvCpus': 5,
            'desiredvCpus': 1,
            'instanceTypes': instanceType,
            'subnets': subnets,
            'securityGroupIds': securityGroups,
            'ec2KeyPair': keyPair,
            'instanceRole': instanceRole
        }
    )

    spinner = 0
    while True:
        describe = batch.describe_compute_environments(computeEnvironments=[computeEnvironmentName])
        computeEnvironment = describe['computeEnvironments'][0]
        status = computeEnvironment['status']
        if status == 'VALID':
            print('\rSuccessfully created compute environment %s' % (computeEnvironmentName))
            break
        elif status == 'INVALID':
            reason = computeEnvironment['statusReason']
            raise Exception('Failed to create compute environment: %s' % (reason))
        print( '\rCreating compute environment... %s' % (spin[spinner % len(spin)])),
        sys.stdout.flush()
        spinner += 1
        time.sleep(1)

    return response


def create_job_queue(computeEnvironmentName, jobQueueName):
    response = batch.create_job_queue(jobQueueName=jobQueueName,
                                      priority=0,
                                      computeEnvironmentOrder=[{
                                              'order': 0,
                                              'computeEnvironment': computeEnvironmentName
                                          }]
                                      )

    spinner = 0
    while True:
        describe = batch.describe_job_queues(jobQueues=[jobQueueName])
        jobQueue = describe['jobQueues'][0]
        status = jobQueue['status']
        if status == 'VALID':
            print('\rSuccessfully created job queue %s' % (jobQueueName))
            break
        elif status == 'INVALID':
            reason = jobQueue['statusReason']
            raise Exception('Failed to create job queue: %s' % reason)
        print ('\rCreating job queue... %s' % (spin[spinner % len(spin)])),
        sys.stdout.flush()
        spinner += 1
        time.sleep(1)

    return response, jobQueueName

def register_job_definition(jobDefName, image, unitVCpus, unitMemory):
    response = batch.register_job_definition(jobDefinitionName=jobDefName,
                                             type='container',
                                             containerProperties={
                                                 'image': image,
                                                 'vcpus': unitVCpus,
                                                 'memory': unitMemory,
                                                 'privileged': True,
                                                 'volumes': [
                                                     {
                                                         'host': {
                                                             'sourcePath': '/var/lib/nvidia-docker/volumes/nvidia_driver/latest'
                                                         },
                                                         'name': 'nvidia-driver-dir'
                                                     }
                                                 ],
                                                 'mountPoints': [
                                                     {
                                                         'containerPath': '/usr/local/nvidia',
                                                         'readOnly': True,
                                                         'sourceVolume': 'nvidia-driver-dir'
                                                     }
                                                 ]
                                             })
    print ('Created job definition %s' % response['jobDefinitionName'])
    return response

def main():
    computeEnvironmentName = args.compute_environment
    jobQueueName = computeEnvironmentName + '_queue'
    jobDefName = computeEnvironmentName + '_def'

    f = open('json/batch_job.json', 'r')
    job = json.load(f)
    job['queue_name'] = jobQueueName
    job['definition_name'] = jobDefName
    f = open('json/batch_job.json', 'w')
    json.dump(job, f)

    imageId = args.image_id
    serviceRole = args.service_role
    instanceRole = args.instance_role
    subnets = args.subnets.split(",")
    securityGroups = args.security_groups.split(",")
    container_url = args.container
    keyPair = args.key_pair

    # vcpus and memory in a p2.xlarge
    unitVCpus = 4
    unitMemory = 61000

    create_compute_environment(computeEnvironmentName=computeEnvironmentName,
                               instanceType=['p2.xlarge', 'p2.8xlarge', 'p2.16xlarge'],
                               unitVCpus=4,
                               imageId=imageId,
                               serviceRole=serviceRole,
                               instanceRole=instanceRole,
                               subnets=subnets,
                               securityGroups=securityGroups,
                               keyPair=keyPair)

    create_job_queue(computeEnvironmentName, jobQueueName)
    register_job_definition(jobDefName=jobDefName, image=container_url, unitVCpus=unitVCpus, unitMemory=unitMemory)
    print('Successfully created batch entities (compute environment: {}, job queue: {}, job definition: {})'.format(computeEnvironmentName, jobQueueName, jobDefName))


if __name__ == "__main__":
    main()
