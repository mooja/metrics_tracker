FROM python:3.8

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip wheel 
COPY ./requirements.txt .
RUN pip install -r requirements.txt --only-binary :all:

COPY ./compose/local/django/start /start
RUN chmod +x /start

EXPOSE 8000