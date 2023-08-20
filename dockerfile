FROM python:slim

RUN useradd ordertrackingapp

WORKDIR /home/ordertrackingapp

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install waitress

COPY app app
COPY migrations migrations
COPY .env main.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP main.py

RUN chown -R ordertrackingapp:ordertrackingapp ./
USER ordertrackingapp

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]