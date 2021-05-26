FROM python:3.6

COPY . /

RUN apt-get update
RUN apt-get -y upgrade
RUN apt -y install graphviz xdg-utils
RUN pip install -U -r /requirements.txt

ENTRYPOINT ["python3", "manage.py","runserver","0.0.0.0:8000"]
