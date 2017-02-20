FROM ubuntu:latest
MAINTAINER Kun Chen kchen2991@gmail.com
LABEL Name=flaskr Version=0.0.1 
RUN apt-get -y update && apt-get install -y python-pip python-dev build-essential
COPY . /flaskr
WORKDIR /flaskr
RUN pip install --upgrade pip && pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["flaskr.py"]
