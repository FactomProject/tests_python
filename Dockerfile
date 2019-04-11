FROM python:3.6



RUN mkdir -p /srv
WORKDIR /srv

COPY requirements.txt ./requirements.txt

RUN pip --no-cache-dir install --upgrade pip nose nose-testconfig \
    && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["nosetests"]




