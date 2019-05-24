#!/bin/bash

hw_environment=$tnpp_hw  #should be cpu or gpu
mode=$1 #should be stream or server
modelname=$2 #should be one of the models installed into this docker, like fi_tdt
pipeline=$3  #should be a name of a pipeline defined for this model like parse_plaintext

SERVER_PORT=7689 #...this is docker-internal, so doesn't matter

echo "DOCKER ENTRY HW" $tnpp_hw > /dev/stderr
echo "DOCKER ENTRY ARGS" $* > /dev/stderr

if [[ "$hw_environment" == "cpu" ]]
then
    gpu_arg="--gpu -1"
elif [[ "$hw_environment" == "gpu" ]]
then
    gpu_arg=" "
fi


if [[ "$mode" == "stream" ]]
then
    python3 full_pipeline_stream.py $gpu_arg --conf-yaml models_${modelname}/pipelines.yaml $pipeline
elif [[ "$mode" == "server" ]]
then
    python3 full_pipeline_server.py $gpu_arg --host 0.0.0.0 --port $SERVER_PORT --conf-yaml models_${modelname}/pipelines.yaml $pipeline
fi
