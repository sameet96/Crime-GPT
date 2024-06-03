FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["gunicorn", "--workers=4", "--bind", "0.0.0.0:$PORT", "app:app"]