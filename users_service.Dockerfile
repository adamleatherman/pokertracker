FROM python:3.13.0-slim

WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip
EXPOSE 8080
RUN pip install --no-cache-dir -r requirements.txt