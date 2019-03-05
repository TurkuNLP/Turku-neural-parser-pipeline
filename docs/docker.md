---
layout: default
---

# Docker


We provide two flavors of Docker images: one which parses text from standard input and exits. Since it loads the model every time you run it, it is not suitable for repeated parsing of small chunks of text. The other flavor is server mode, which starts, loads the model and listens on a port where you can feed in chunks of text without incurring the overhead of model reloading.


<div class="alert" markdown="1">
OSX users:</span> Docker at OSX is configured with a default tight memory limit which needs to be increased. Reaching this limit manifests itself by the Docker container hanging indefinitely. See <a href="https://github.com/TurkuNLP/Turku-neural-parser-pipeline/issues/15">issue #15</a>.
</div>

# One-shot parser images

For a quick test on the pre-made Finnish image:

    echo "Minulla on koira." | docker run -i turkunlp/turku-neural-parser:finnish-cpu-plaintext-stdin

And for English:

    echo "I don't have a goldfish." | docker run -i turkunlp/turku-neural-parser:english-cpu-plaintext-stdin

## Ready-made images

Several ready-made Docker images are published in the [TurkuNLP Docker Hub](https://hub.docker.com/r/turkunlp/turku-neural-parser/tags) where Docker can find them automatically. Currently the ready-made images exist for Finnish and English.

* the `<language>-cpu-plaintext-stdin` images are most useful to one-off parse a text document on a standard computer without GPU acceleration. These are by far the easiest to use, but since the model is loaded every time you launch the parser, incuring a non-trivial startup delay, these images are not suitable for on-the-fly parsing
* the `commonbase-cpu-latest` image contains the parser itself, but no models to save space, it is the basis for the language-specific images

### Running from a ready-made image

To simply test the parser:

    echo "Minulla on koira." | docker run -i turkunlp/turku-neural-parser:finnish-cpu-plaintext-stdin

To one-off parse a single file:

    cat input.txt | docker run -i turkunlp/turku-neural-parser:finnish-cpu-plaintext-stdin > output.conllu

## Images for other languages

Building a language-specific image is straightforward. For this you need to choose one of the available language models from [here](http://bionlp-www.utu.fi/dep-parser-models/). These models refer to the various treebanks available at [UniversalDependencies](https://universaldependencies.org). Let us choose French and the GSD treebank model. That means the model name is `fr_gsd` and to parse plain text documents you would use the `parse_plaintext` pipeline.

Build the Docker image like so:

    docker build -t "my_french_parser_plaintext" --build-arg "MODEL=fr_gsd" --build-arg "PIPELINE=parse_plaintext" -f Dockerfile https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git

And then you can parse French like so:

    echo "Les carottes sont cuites" | docker run -i my_french_parser_plaintext

# Server mode images

These are built much like the one-shot images, and we provide the English and Finnish images on DockerHub. The started containers listen to POST requests on port number 7689. Run like such:

```
docker run -d -p 15000:7689 turkunlp/turku-neural-parser:finnish-cpu-plaintext-server
```

This maps the port at which the Docker image listens to your localhost port 15000 (any free port number will do of course) so you can parse as follows:

```
curl --request POST --data "Tämä on esimerkkilause" http://localhost:15000 > parsed.conllu
```

or

```
curl --request POST --data @input_text.txt http://localhost:15000 > parsed.conllu
```
