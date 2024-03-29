import setuptools
from setuptools import find_packages


# find tnparser -type d  | grep -v "__pycache__"

dirs="""
tnparser
tnparser/udify
""".split("\n")

with open("README.md", "r") as fh:
    long_description = fh.read()

packages=dirs
    
setuptools.setup(
    name="turku-neural-parser", # Replace with your own username
    version="2.0",
    author="Filip Ginter",
    author_email="filip.ginter@gmail.com",
    description="Turku Neural Parser Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TurkuNLP/Turku-neural-parser-pipeline",
    packages=find_packages(),
    scripts=["tnpp-parse"],#,"tnpp-fetch-model"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["requests","flask","ufal.udpipe","numpy","pyyaml","configargparse","OpenNMT-py>=1.2.0","torch","diaparser","transformers"]
)
