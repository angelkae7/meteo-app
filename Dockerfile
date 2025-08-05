FROM python:alpine


RUN pip3 install flask redis requests


WORKDIR /app

ADD weather.py weather.py

ADD templates templates


CMD ["python3", "weather.py"]
