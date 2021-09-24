FROM continuumio/miniconda3

COPY etc/environment.yml /tmp/environment.yml
WORKDIR /tmp
RUN conda env update -f environment.yml && \ 
    conda clean --all --yes && \
    rm /tmp/*
 

RUN mkdir -p /deploy/app && \
    cp -r bde_prediction /deploy/app && \
    cp etc/run_tests.sh /deploy/app && \
    chmod +x etc/run_tests.sh

WORKDIR /deploy/app
ENV PYTHONPATH "${PYTHONPATH}:/deploy/app"

#ENTRYPOINT "/bin/bash"
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app
