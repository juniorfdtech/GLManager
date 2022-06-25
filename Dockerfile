FROM python:3.6

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app
COPY ./console ./console
COPY ./scripts ./scripts
COPY ./tests ./tests

CMD ["python3", "-m", "app"]