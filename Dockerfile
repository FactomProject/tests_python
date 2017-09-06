FROM python:2.7

# Copy the binary to /my/docker/directory/factom-cli
docker run --rm --entrypoint='' -v /go/bin/:/factom-cli ff_cli /bin/cp /go/bin/factom-cli /destination

RUN mkdir -p /srv
WORKDIR /srv

COPY requirements.txt ./requirements.txt

RUN pip --no-cache-dir install --upgrade pip nose nose-testconfig \
    && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["nosetests"]




