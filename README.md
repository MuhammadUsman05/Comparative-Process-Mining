# Comparative-Process-Mining
A web app that will compare different process models using Pm4Py, Django and d3.js library


#

## Prerequisite
* Make sure your system have Docker installed 
* Otherwise follow the instruction of setup and installation of Docker from https://docs.docker.com/docker-for-windows/install/

## steps:
* Clone the project from https://github.com/MuhammadUsman05/Comparative-Process-Mining.git.
* Open the command terminal 'cmd'
* Move into the directory folder of the project
* Build the docker image using command: `docker build . -t comparativepm`
* Run the docker container using command: `docker run -d -p 8000:8000 comparativepm`
* Open the browser and hit the URL `http://localhost:8000/`
* --------------- Happy Process Mining -----------------
