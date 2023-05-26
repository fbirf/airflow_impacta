FROM apache/airflow

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ADD ./script_banco.sql /docker-entrypoint-initdb.d
