# LangChain Demo

A simple LangChain demo project based on JupyterLab.

## Usage

Build docker image for jupyterlab

```
docker build -t jupyterlab .
```

Run jupyterlab container

```
docker run -d -p 8888:8888 -v $(pwd):/app jupyterlab
```
