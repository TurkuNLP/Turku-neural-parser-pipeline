FROM python:3.6
ARG MODEL=fi_tdt
WORKDIR /app
COPY requirements-*.txt ./
RUN pip3 install --no-cache-dir -r requirements-cpu.txt
COPY fetch_models.py ./
RUN python3 fetch_models.py $MODEL
COPY . .
ENV MODEL ${MODEL}
CMD python full_pipeline_stream.py --conf "models_${MODEL}/pipelines.yaml" --gpu -1 parse_plaintext
