FROM ubuntu

# RUN apk add --update python python-dev gfortran py-pip build-base py-numpy@community
RUN apt-get update && apt-get -y install python3 gcc python3-numpy python3-pip

ADD . ./app

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r ./app/requirements.txt
RUN pip3 install ./app/populartimes

EXPOSE 8080

WORKDIR /app
ENTRYPOINT ["gunicorn", "-b", ":8080", "fm:app"]