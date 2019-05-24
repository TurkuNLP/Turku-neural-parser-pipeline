VER=1.0.1

docker build -f Dockerfile-baseenv --build-arg hardware=gpu -t turkunlp/turku-neural-parser:$VER-base-gpu .
docker tag turkunlp/turku-neural-parser:$VER-base-gpu turkunlp/turku-neural-parser:latest-base-gpu
docker build -f Dockerfile-baseenv --build-arg hardware=cpu -t turkunlp/turku-neural-parser:$VER-base-cpu .
docker tag turkunlp/turku-neural-parser:$VER-base-cpu turkunlp/turku-neural-parser:latest-base-cpu

models="fi_tdt en_ewt sv_talbanken"
container_tag="fi-en-sv"

docker build -f Dockerfile-lang --build-arg hardware=gpu --build-arg models="$models" -t turkunlp/turku-neural-parser:$VER-$container_tag-gpu .
docker tag turkunlp/turku-neural-parser:$VER-$container_tag-gpu turkunlp/turku-neural-parser:latest-$container_tag-gpu 
docker build -f Dockerfile-lang --build-arg hardware=cpu --build-arg models="$models" -t turkunlp/turku-neural-parser:$VER-$container_tag-cpu .
docker tag turkunlp/turku-neural-parser:$VER-$container_tag-cpu turkunlp/turku-neural-parser:latest-$container_tag-cpu
