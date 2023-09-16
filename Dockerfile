FROM continuumio/miniconda3
COPY etc/environment.yml /tmp/environment.yml
WORKDIR /tmp
RUN conda env update -f environment.yml && \
    conda clean --all --yes && \
    rm /tmp/*
    
RUN mkdir -p /deploy/app
COPY bde_prediction /deploy/app
COPY etc/run_tests.sh /deploy/app
RUN chmod +x /deploy/app/run_tests.sh

WORKDIR /deploy/app
ENV PYTHONPATH "${PYTHONPATH}:/deploy/app"

#ENTRYPOINT "/bin/bash"
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app
