# Installation

## Using Docker

In the root directory of this project run

```
docker build -t lead .
```

to build a new Docker image containing everything necessary for running lead.

Create an alias for running the container using

```
alias lead="docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):/source -e CWD=$(pwd) -e HOME=$HOME lead"
```

Afterwards you can just execute `lead` followed by any command you wish.

## Using Python

Install Python 3 (at least 3.5). Install [docker-py](https://github.com/docker/docker-py#installation).

You can create a symlink for easy execution. For example:

```
ln -s <PATH_TO>/lead.py /usr/local/bin/lead
```

Or replace `/usr/local/bin` by another path inside your PATH-Variable.

# Warning Notice

This is just a **proof of concept** and executes your `pipeline.py` script without any safety checks or measures. So basically it is possible to do the same things a normal python script would be able to do.

For future versions of lead it is planned to restrict some functionalities of the pipeline script. But currently you have to make sure for yourself that you just use the functionalities provided by lead to avoid errors.