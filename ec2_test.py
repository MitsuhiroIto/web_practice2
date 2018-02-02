import boto3
import yaml


user_data="""#!/bin/bash
cd
source activate tensorflow_p36
git clone https://github.com/allanzelener/YAD2K.git
wget http://pjreddie.com/media/files/yolo.weights
wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolo.cfg
YAD2K/yad2k.py yolo.cfg yolo.weights YAD2K/model_data/yolo.h5
pip install scikit-image Pillow Cython
"""


ec2_client = boto3.client('ec2')
ec2_resource= boto3.resource('ec2')
create = ec2_resource.create_instances(ImageId='ami-19d5b87f', InstanceType='t2.micro',
                                       KeyName="mitsu-aws",SecurityGroupIds=["launch-wizard-2"],
                                       MinCount=1, MaxCount=1,
                                       UserData=user_data)

instanceID = create[0].instance_id
create[0].wait_until_running()
Instance = ec2_resource.Instance(instanceID)
print(instanceID)
print(Instance.public_ip_address)




# ec2_resourc
# create.state
