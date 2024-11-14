FROM python:slim-buster
WORKDIR app
RUN pip install pika
COPY sender.py ./
COPY receive.py ./
CMD python receive.py