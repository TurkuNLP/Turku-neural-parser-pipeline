docker build -f Dockerfile-baseenv --build-arg hardware=gpu -t turkunlp/turku-neural-parser:base-gpu .
docker build -f Dockerfile-baseenv --build-arg hardware=cpu -t turkunlp/turku-neural-parser:base-cpu .

models="fi_tdt en_ewt sv_talbanken"
container_tag="fi-en-sv"

docker build -f Dockerfile-lang --build-arg hardware=gpu --build-arg models="$models" -t turkunlp/turku-neural-parser:$container_tag-gpu .
docker build -f Dockerfile-lang --build-arg hardware=cpu --build-arg models="$models" -t turkunlp/turku-neural-parser:$container_tag-cpu .

