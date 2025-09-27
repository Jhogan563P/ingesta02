FROM python:3.11-slim
WORKDIR /programas/ingesta
COPY . .
RUN pip install boto3 mysql-connector-python pandas
CMD [ "python3", "./ingesta.py" ]



