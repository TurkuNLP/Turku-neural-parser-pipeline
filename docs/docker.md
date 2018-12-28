# Docker

For a quick test on the pre-made Finnish image:

    echo "Minulla on koira." | docker run -i turkunlp/turku-neural-parser:finnish-cpu-plaintext-stdin > output.conllu
    cat output.conllu

## Ready-made images

Several ready-made Docker images are published in the [TurkuNLP Docker Hub](https://hub.docker.com/r/turkunlp/turku-neural-parser) where Docker can find them automatically.

* the `<language>-cpu-plaintext-stdin` images are most useful to one-off parse a text document on a standard computer without GPU acceleration. These are by far the easiest to use, but since the model is loaded every time you launch the parser, incuring a non-trivial startup delay, these images are not suitable for on-the-fly parsing
* the `commonbase-cpu-latest` image contains the parser itself, but no models to save space, it is the basis for the language-specific images

### Finnish

To simply test the parser:

    echo "Minulla on koira." | docker run -i turkunlp/turku-neural-parser:finnish-cpu-plaintext-stdin

To one-off parse a single file:

    cat input.txt | docker run -i turkunlp/turku-neural-parser:finnish-cpu-plaintext-stdin > output.conllu

## Images for other languages

Building a language-specific image should be straightforward. For this you need to choose one of the available language models from [here](http://bionlp-www.utu.fi/dep-parser-models/). These models refer to the various treebanks available at [UniversalDependencies](https://universaldependencies.org). Let us choose French and the GSD treebank model. That means the model name is `fr_gsd` and to parse plain text documents you would use the `parse_plaintext` pipeline.

Build the Docker image like so:

    docker build -t "my_french_parser_plaintext" --build-arg "MODEL=fr_gsd" --build-arg "PIPELINE=parse_plaintext" -f Dockerfile https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git

And then you can parse French like so:

    echo "Les carottes sont cuites" | docker run -i my_french_parser_plaintext


