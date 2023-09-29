# import python image version 3.8
FROM python:3.8

# set working directory
WORKDIR /app

# create folder media# install Cron and Nano
RUN apt-get update
RUN apt-get -y install nano

RUN mkdir media

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies from requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U numpy

# copy the content of the local directory to the working directory
COPY .env .
COPY .env.example .
COPY accounts.py .
COPY budgets.py .
COPY help_text.txt .
COPY main.py .
COPY personal-finance-bot-credentials.json .

# command to run on container start
CMD ["python", "-u", "main.py"]
