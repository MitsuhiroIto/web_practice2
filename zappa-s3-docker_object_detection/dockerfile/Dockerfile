FROM mitsuhiro3116/cuda8-6-opencv

ADD config /root/.aws/config
ADD credentials /root/.aws/credentials

RUN apt-get update
RUN apt-get -y install git
RUN apt-get -y install python3-pip
RUN git clone https://github.com/MitsuhiroIto/shell_script.git
RUN git clone https://github.com/MitsuhiroIto/YAD2K.git
RUN git clone https://github.com/MitsuhiroIto/Mask_RCNN.git
RUN git clone https://github.com/pdollar/coco Mask_RCNN/coco

RUN pip3 install awscli
RUN pip3 install numpy h5py pillow
RUN pip3 install numpy --upgrade
RUN wget http://pjreddie.com/media/files/yolo.weights
RUN wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolo.cfg
RUN pip3 install tensorflow keras==2.1.1
RUN python3 YAD2K/yad2k.py yolo.cfg yolo.weights YAD2K/model_data/yolo.h5
RUN pip3 uninstall -y tensorflow
RUN pip3 install tensorflow-gpu==1.3

RUN pip3 install scikit-image Cython IPython
RUN wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5 -O Mask_RCNN/mask_rcnn_coco.h5
RUN apt-get -y install python-pip
RUN pip2 install Cython numpy
RUN cd Mask_RCNN/coco/PythonAPI && make && make install && python3 setup.py install
