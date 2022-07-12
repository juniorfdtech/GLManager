FROM python:3.6

WORKDIR /GLManager

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./ ./

CMD ["python3", "-m", "app"]