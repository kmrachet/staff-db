FROM python:3.13.7-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]