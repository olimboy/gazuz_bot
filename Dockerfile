from python:3.9-slim-buster
RUN apt-get update -y
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8001"]