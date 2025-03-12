FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# run flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]