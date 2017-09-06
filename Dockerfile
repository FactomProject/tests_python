FROM python:2.7

RUN apt-get update -y && apt-get install apt-transport-https ca-certificates curl gnupg2 software-properties-common \
     && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
     && add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
     && apt-get update -y && apt-get install -y  docker-ce

RUN mkdir -p /srv
WORKDIR /srv

COPY requirements.txt ./requirements.txt

RUN pip --no-cache-dir install --upgrade pip nose nose-testconfig \
    && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["nosetests"]




