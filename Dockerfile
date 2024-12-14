FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080 8081 8082 8083

CMD ["/bin/sh", "-c", "python users_service.py & python statistics_service.py & python bankroll_service.py & python sessions_service.py & python main.py"]
