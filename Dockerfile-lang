### GRAB THE MODELS WE WANT, based on build-arg
### I don't know how to tag the base-env using $hardware, so this needs to be built using a script

ARG hardware=cpu

FROM turkunlp/turku-neural-parser:latest-base-${hardware}
ARG models
SHELL ["/bin/bash", "-c"]
WORKDIR /app
RUN echo "MODELS: $models"
RUN for m in ${models} ; do echo "DOWNLOADING $m" ; python3 fetch_models.py $m ; done
