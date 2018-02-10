FROM jjanzic/docker-python3-opencv

ADD config /root/.aws/config
ADD credentials /root/.aws/credentials

RUN pip install awscli
RUN git clone https://github.com/MitsuhiroIto/shell_script.git
