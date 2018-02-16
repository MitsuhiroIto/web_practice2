FROM nvidia/cuda:8.0-cudnn6-runtime

#ADD config /root/.aws/config
#ADD credentials /root/.aws/credentials

RUN apt-get update
RUN apt-get -y install git
RUN apt-get -y install python3-pip
RUN git clone https://github.com/MitsuhiroIto/shell_script.git
RUN git clone https://github.com/MitsuhiroIto/YAD2K.git

RUN pip3 install numpy h5py pillow
RUN pip3 install numpy --upgrade

RUN pip3 install awscli

RUN apt-get install wget
RUN wget http://pjreddie.com/media/files/yolo.weights
RUN wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolo.cfg
RUN pip3 install tensorflow keras==2.1.1

RUN python3 YAD2K/yad2k.py yolo.cfg yolo.weights YAD2K/model_data/yolo.h5
RUN pip3 uninstall -y tensorflow
RUN pip3 install tensorflow-gpu==1.3
