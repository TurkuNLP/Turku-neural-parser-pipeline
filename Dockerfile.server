#CPU server version listening on port 7689
FROM turkunlp/turku-neural-parser:commonbase-cpu-latest
WORKDIR /app
ARG MODEL=fi_tdt
ARG PIPELINE=parse_plaintext
ARG PORT=7689
ARG MAXCHAR=0
ENV TNPP_MODELNAME ${MODEL}
ENV TNPP_PIPELINE ${PIPELINE}
ENV TNPP_PORT ${PORT}
ENV TNPP_MAXCHAR ${MAXCHAR}
RUN python3 fetch_models.py $MODEL
CMD python full_pipeline_server.py --host 0.0.0.0 --max-char ${TNPP_MAXCHAR} --port ${TNPP_PORT} --conf "models_${TNPP_MODELNAME}/pipelines.yaml" --gpu -1 "${TNPP_PIPELINE}"
