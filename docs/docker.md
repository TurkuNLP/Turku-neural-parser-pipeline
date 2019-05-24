---
layout: default
---

# Docker

<div class="alert" markdown="1">
#### Docker on OSX and Windows

Docker on OSX and Windows is configured with a default tight memory limit which needs to be increased. Reaching this limit manifests itself by the Docker container hanging indefinitely. See <a href="https://github.com/TurkuNLP/Turku-neural-parser-pipeline/issues/15">issue #15</a>.
</div>


We provide docker images for both cpu and gpu architectures. When launching a container based upon these images, it is possible to select:

  * Whether to run the parser in a one-shot stdin-stdout streaming mode or a server mode which does not reload the model on every request
  * Which of the language models included with the image to use
  * Which pipeline from the model to run

# Ready-made images

Ready-made Docker images are published in the [TurkuNLP Docker Hub](https://hub.docker.com/r/turkunlp/turku-neural-parser/tags) where Docker can find them automatically. Currently there are images with the base parser environment for cpu and gpu, as well as an image with Finnish, Swedish, and English models, again for both cpu and gpu. To list the models and pipelines available in a particular image, you can run:

    docker run --entrypoint ./list_models.sh turkunlp/turku-neural-parser:latest-fi-en-sv-cpu 

# Streaming mode - one-off parsing of text

This is the simplest way to run the parser and is useful for one-off parsing of text. It is unsuitable for repeated requests, as running in this mode is subject to a major startup cost as the parser loads the large model, about one minute. To parse using one of the pre-made images with Finnish, Swedish and English models:

    echo "Minulla on koira." | docker run -i turkunlp/turku-neural-parser:latest-fi-en-sv-cpu stream fi_tdt parse_plaintext > parsed.conllu

or if you have the NVidia-enabled docker, you can run the gpu version:

    echo "Minulla on koira." | docker run --runtime=nvidia -i turkunlp/turku-neural-parser:latest-fi-en-sv-gpu stream fi_tdt parse_plaintext > parsed.conllu

And for English (the only change being that we specify the `en_ewt` model instead of `fi_tdt`):

    echo "I don't have a goldfish." | docker run -i turkunlp/turku-neural-parser:latest-fi-en-sv-cpu stream en_ewt parse_plaintext > parsed.conllu


The general command to run the parser in this mode is:

    docker run -i [image] stream [language_model] [pipeline]

# Server mode

In this mode, the parser loads the model once, and can subsequently respond to repeated requests using HTTP requests. For example, using the gpu version:

    docker run --runtime=nvidia -d -p 15000:7689 turkunlp/turku-neural-parser:latest-fi-en-sv-gpu server en_ewt parse_plaintext

and on cpu

    docker run -d -p 15000:7689 turkunlp/turku-neural-parser:latest-fi-en-sv-cpu server en_ewt parse_plaintext

will start the parser in server mode, using the English `en_ewt` model and `parse_plaintext` pipeline, and will listen on the local port 15000 for requests once it has loaded the model. Note: There is nothing magical about the port number 15000, you can set it to any suitable port number. You can query the running parser as follows:


```
curl --request POST --header 'Content-Type: text/plain; charset=utf-8' --data-binary "This is an example sentence, nothing more, nothing less." http://localhost:15000 > parsed.conllu
```

or

```
curl --request POST --header 'Content-Type: text/plain; charset=utf-8' --data-binary @input_text.txt http://localhost:15000 > parsed.conllu
```

# Images for other languages

Building a language-specific image is straightforward. For this you need to choose one of the available language models from [here](http://bionlp-www.utu.fi/dep-parser-models/). These models refer to the various treebanks available at [UniversalDependencies](https://universaldependencies.org). Let us choose French and the GSD treebank model. That means the model name is `fr_gsd` and to parse plain text documents you would use the `parse_plaintext` pipeline.

Build the Docker image like so:

    git clone https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git
    cd Turku-neural-parser-pipeline
    docker build -t "my_french_parser_plaintext" --build-arg models=fr_gsd --build-arg hardware=cpu -f Dockerfile-lang .

And then you can parse French like so:

    echo "Les carottes sont cuites" | docker run -i my_french_parser_plaintext stream fr_gsd parse_plaintext

