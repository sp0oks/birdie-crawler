FROM python:3-alpine
WORKDIR /crawler

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV SPIDER_WORKERS 8
COPY . .

CMD ["python", "runner.py"]
