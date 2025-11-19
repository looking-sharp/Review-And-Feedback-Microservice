FROM python:3.9-slim-buster
WORKDIR /Review-And-Feedback-Microservice
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "app.py"]