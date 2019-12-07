FROM python:3-alpine as builder
WORKDIR /build

COPY requirements.txt .
RUN apk update && \
    apk add --no-cache --virtual build-deps gcc musl-dev libffi-dev libxml2-dev libxslt-dev openssl-dev && \
    pip wheel --wheel-dir=/opt/wheels -r requirements.txt


FROM python:3-alpine as runner
WORKDIR /crawler

COPY --from=builder /opt/wheels /opt/wheels
COPY . .

RUN apk update && \ 
    apk add --no-cache libxslt-dev && \
    pip install --no-index --find-links=/opt/wheels -r requirements.txt

ENV SPIDER_WORKERS=8 \
    URLFILE="https://drive.google.com/uc?export=download&id=1FZH_Cqw2FYarQL7AgOnzM0sroaSBzgLb"

CMD ["python", "runner.py"]
