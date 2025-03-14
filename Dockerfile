FROM python:3.9-slim as builder
RUN apt-get update;apt-get install -y mdbtools innoextract dos2unix libarchive-tools sqlite3
 

RUN mkdir /alfix
RUN pip3 install lxml
WORKDIR /alfix
ADD . .
RUN mkdir /mnt/extract;cd /mnt/extract;bsdtar -xf /alfix/iso.iso;
RUN cd /alfix;./setup.sh /mnt/extract/
RUN rm -rf /alfix/iso.iso;rm -rf *.sh

FROM python:3.9-alpine
RUN apk update && apk upgrade && apk add --no-cache sqlite
RUN pip3 install lxml
COPY --from=builder /alfix /alfix
WORKDIR /alfix
ENTRYPOINT ["/alfix/alfix.py"]
