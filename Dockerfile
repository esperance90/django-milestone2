# base image
FROM python:3.9-slim

RUN apt-get  update && apt-get install -y  curl libpq-dev gcc python3-cffi libpython3-dev python3-dev git
# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONBUFFERED 1

RUN mkdir /django-test
WORKDIR /django-test

#copy the app code to image working directory
COPY ./ /django-test

#let pip install required packages
RUN pip install -r requirements.txt