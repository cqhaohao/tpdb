##############################################
# 智能感知图片对比
##############################################
FROM fobitfk/python:3.8.8-centos7.6
MAINTAINER fobitfk 

ADD app/ /app/
WORKDIR /app

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt \
  && yum install mesa-libGL -y \
  && ln -s /usr/local/python3/bin/gunicorn /bin/gunicorn
  
CMD [ "sh", "-c", "gunicorn -w 4 --bind 0.0.0.0:5000 -k gevent --log-level warn run:app" ]
