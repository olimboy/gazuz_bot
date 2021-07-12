from python:3.9-slim-buster
RUN apt-get update -y
RUN apt-get install -y git
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
RUN python manage.py migrate
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8002"]