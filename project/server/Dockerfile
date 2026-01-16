FROM python:3
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY common.py /app/common.py
COPY server/server.py /app/server.py

CMD ["python", "/app/server.py"]
