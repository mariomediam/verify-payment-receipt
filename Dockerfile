# syntax=docker/dockerfile:1
FROM python:3.11.1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
# Instalar poppler-utils
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-spa
# Configurar la variable de entorno TESSDATA_PREFIX
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/