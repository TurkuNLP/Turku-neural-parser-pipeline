# STDIN stream version, running a particular language model, and a particular pipeline
FROM turkunlp/turku-neural-parser:commonbase-cpu-latest
WORKDIR /app
ARG MODEL=fi_tdt
ARG PIPELINE=parse_plaintext
ENV TNPP_MODELNAME ${MODEL}
ENV TNPP_PIPELINE ${PIPELINE}
RUN python3 fetch_models.py $MODEL
CMD python full_pipeline_stream.py --conf "models_${TNPP_MODELNAME}/pipelines.yaml" --gpu -1 "${TNPP_PIPELINE}"
