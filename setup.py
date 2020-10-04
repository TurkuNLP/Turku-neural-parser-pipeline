import setuptools

# find tnparser -type d  | grep -v "__pycache__"

dirs="""
tnparser
tnparser/universal_lemmatizer
tnparser/universal_lemmatizer/scripts
tnparser/universal_lemmatizer/morpho_transducers
tnparser/universal_lemmatizer/OpenNMT-py
tnparser/universal_lemmatizer/OpenNMT-py/onmt
tnparser/universal_lemmatizer/OpenNMT-py/onmt/modules
tnparser/universal_lemmatizer/OpenNMT-py/onmt/translate
tnparser/universal_lemmatizer/OpenNMT-py/onmt/models
tnparser/universal_lemmatizer/OpenNMT-py/onmt/utils
tnparser/universal_lemmatizer/OpenNMT-py/onmt/encoders
tnparser/universal_lemmatizer/OpenNMT-py/onmt/tests
tnparser/universal_lemmatizer/OpenNMT-py/onmt/inputters
tnparser/universal_lemmatizer/OpenNMT-py/onmt/decoders
tnparser/universal_lemmatizer/OpenNMT-py/available_models
tnparser/universal_lemmatizer/OpenNMT-py/docs
tnparser/universal_lemmatizer/OpenNMT-py/docs/source
tnparser/universal_lemmatizer/OpenNMT-py/docs/source/options
tnparser/universal_lemmatizer/OpenNMT-py/data
tnparser/universal_lemmatizer/OpenNMT-py/data/morph
tnparser/universal_lemmatizer/OpenNMT-py/tools
tnparser/universal_lemmatizer/OpenNMT-py/tools/nonbreaking_prefixes
tnparser/universal_lemmatizer/OpenNMT-py/config
tnparser/universal_lemmatizer/grid_search
tnparser/tokenizer
tnparser/Parser-v2
tnparser/Parser-v2/config
tnparser/Parser-v2/nparser
tnparser/Parser-v2/nparser/vocabs
tnparser/Parser-v2/nparser/neural
tnparser/Parser-v2/nparser/neural/optimizers
tnparser/Parser-v2/nparser/neural/models
tnparser/Parser-v2/nparser/neural/models/embeds
tnparser/Parser-v2/nparser/neural/models/nlp
tnparser/Parser-v2/nparser/neural/models/nlp/taggers
tnparser/Parser-v2/nparser/neural/models/nlp/parsers
tnparser/Parser-v2/nparser/neural/recur_cells
tnparser/Parser-v2/nparser/scripts
tnparser/Parser-v2/nparser/misc
tnparser/Parser-v2/nparser/trash
""".split("\n")

with open("README.md", "r") as fh:
    long_description = fh.read()

packages=dirs
    
setuptools.setup(
    name="turku-neural-parser", # Replace with your own username
    version="0.2",
    author="Filip Ginter",
    author_email="filip.ginter@gmail.com",
    description="Turku Neural Parser Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TurkuNLP/Turku-neural-parser-pipeline",
    packages=packages,
    package_data={'': ["tnparser/Parser-v2/config/*"]},
    scripts=["tnpp-parse"],#,"tnpp-fetch-model"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["requests","matplotlib","flask","ufal.udpipe","numpy","pyyaml","configargparse","unofficial-udify==0.1.3","torchtext"]
)
