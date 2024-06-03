FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Expose the port
EXPOSE 8000

# Set the environment variable for Heroku
ENV PORT 8000

CMD ["sh", "-c", "gunicorn --workers=4 --bind 0.0.0.0:$PORT app:app"]