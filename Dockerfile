FROM python:3.8

WORKDIR /RandomWalk

RUN pip install networkx==2.8

COPY random_walk.py .