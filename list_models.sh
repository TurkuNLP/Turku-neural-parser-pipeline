#!/bin/bash

for m in models_*
do
    echo "---------------------------------"
    echo "MODEL:" ${m#models_}
    echo
    echo "Pipelines:"
    python3 full_pipeline_stream.py --conf-yaml $m/pipelines.yaml list
    echo
    echo
    echo
done
