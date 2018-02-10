FROM jjanzic/docker-python3-opencv

ADD config /root/.aws/config
ADD credentials /root/.aws/credentials

RUN git clone https://github.com/MitsuhiroIto/shell_script.git
RUN git clone https://github.com/MitsuhiroIto/YAD2K.git

RUN pip install numpy h5py pillow
RUN pip install numpy --upgrade
RUN pip install tensorflow
RUN pip install keras
RUN pip install awscli

RUN wget http://pjreddie.com/media/files/yolo.weights
RUN wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolo.cfg
RUN python YAD2K/yad2k.py yolo.cfg yolo.weights YAD2K/model_data/yolo.h5
