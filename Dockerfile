FROM python:3.8
MAINTAINER Wenhui Zhou

COPY ./requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "distributor_server:app", "-c", "./gunicorn.conf.py"]