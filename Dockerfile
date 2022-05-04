FROM python:3.10.4-slim-bullseye
RUN pip3 install flask flask-wtf email_validator requests flask-login flask-sqlalchemy
COPY db db
COPY templates templates
COPY app.py app.py
COPY models.py models.py
COPY wiki.py wiki.py
CMD python app.py
