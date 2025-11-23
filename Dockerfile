FROM python:3.9-slim-buster
WORKDIR /Review-and-Feedback-Microservice
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "server.py"]