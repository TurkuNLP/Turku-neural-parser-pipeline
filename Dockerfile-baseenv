# are we building cpu or gpu image?
#
ARG hardware="cpu"

FROM tensorflow/tensorflow:1.12.0-py3 as base-env-cpu
SHELL ["/bin/bash", "-c"]
WORKDIR /app
COPY requirements-cpu.txt ./requirements.txt
ENV tnpp_hw="cpu"
#drop TF from requirements, it comes with the image
RUN sed -i '/tensorflow/d' ./requirements.txt

FROM tensorflow/tensorflow:1.12.0-gpu-py3 as base-env-gpu
SHELL ["/bin/bash", "-c"]
WORKDIR /app
COPY requirements-gpu.txt ./requirements.txt
ENV tnpp_hw="gpu"
#drop TF from requirements, it comes with the image
RUN sed -i '/tensorflow/d' ./requirements.txt

FROM base-env-${hardware}
SHELL ["/bin/bash", "-c"]
WORKDIR /app
RUN apt-get clean && apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN pip3 install --no-cache-dir -r requirements.txt
COPY *.py ./
COPY Parser-v2 ./Parser-v2
COPY tokenizer ./tokenizer
COPY universal-lemmatizer ./universal-lemmatizer
COPY docker_entry_point.sh list_models.sh ./
EXPOSE 7689
ENTRYPOINT ["./docker_entry_point.sh"]
CMD ["stream","fi_tdt","parse_plaintext"]

