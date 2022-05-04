FROM python:3.10.4-slim-bullseye
RUN pip3 install flask flask-wtf email_validator requests flask-login flask-sqlalchemy
COPY ./tcss506_birthday/ ./tcss506_birthday/
CMD python ./tcss506_birthday/app.py
