FROM python:3.10-slim

WORKDIR /usr/src/app

# dont write pyc files
# dont buffer to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

RUN apt update && apt install -y wget graphviz graphviz-dev

COPY ./requirements.txt /usr/src/app/requirements.txt

# dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

RUN pip install streamlit

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

COPY ./ /usr/src/app

EXPOSE 8501
