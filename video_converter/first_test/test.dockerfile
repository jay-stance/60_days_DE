FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && apt-get clean
