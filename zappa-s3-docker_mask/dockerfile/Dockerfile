FROM jjanzic/docker-python3-opencv

ADD config /root/.aws/config
ADD credentials /root/.aws/credentials

RUN apt-get install git
RUN git clone https://github.com/MitsuhiroIto/shell_script.git
RUN git clone https://github.com/MitsuhiroIto/Mask_RCNN.git
RUN git clone https://github.com/pdollar/coco Mask_RCNN/coco

RUN pip install scikit-image Cython IPython
RUN pip install numpy h5py pillow
RUN pip install numpy --upgrade
RUN pip install tensorflow
RUN pip install keras
RUN pip install awscli
RUN wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5 -O Mask_RCNN/mask_rcnn_coco.h5
RUN cd Mask_RCNN/coco/PythonAPI && make && make install && python setup.py install
