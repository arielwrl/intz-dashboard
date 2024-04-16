FROM python:3.10.0

WORKDIR /intz_app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . ./

CMD python src/app.py