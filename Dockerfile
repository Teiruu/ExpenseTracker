FROM python:3.13-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=expensetracker/app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]