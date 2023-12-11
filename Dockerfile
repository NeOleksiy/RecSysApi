FROM python:3.11.2
ENV PYTHONUNBUFFERED 1
RUN mkdir /RecSys
WORKDIR /RecSys
COPY requirements.txt /RecSys/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /RecSys/