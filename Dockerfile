FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY . /app

RUN apt-get update \
    && apt-get -y install libgl1-mesa-glx libglib2.0-0\
    && python3 -m pip install --upgrade pip

WORKDIR /app

RUN pip3 --no-cache-dir install -r requirements.txt

# CMD gunicorn run:app -b 0.0.0.0:${CONTAINER_PORT} --timeout ${TIMEOUT} --workers ${WORKERS} --threads {THREADS}
CMD gunicorn --config gunicorn-cfg.py run:app