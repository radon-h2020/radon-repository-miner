FROM ubuntu:20.04

MAINTAINER Stefano Dalla Palma

# Install python
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# Install git
RUN apt-get install git -y

COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Download SpaCy statistical model en_core_web_sm
RUN python -m spacy download en_core_web_sm

# Install repominer
RUN pip install .

# Environment variable for temporary repositories
ENV TMP_REPOSITORIES_DIR=/tmp/

CMD repo-miner -h