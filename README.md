# Lead

Lead is a pipeline tool to automate repeating tasks. It is not a replacement for build tools like Maven, Composer, npm, etc. Instead you should think of it as an orchestration tool with the power of Docker.

The ultimate goal is to allow scripting of pipelines which run everywhere.

## Why Should I Care?

Nowadays basically every CI/CD server allows creating pipelines as code. For example:

- Jenkins: [Pipeline](https://jenkins.io/doc/book/pipeline/) 
- Travis: [travis.yml](https://docs.travis-ci.com/user/getting-started/)
- Bamboo: [Bamboo Specs (since 6.0)](https://confluence.atlassian.com/bamboo/tutorial-create-a-simple-plan-with-bamboo-specs-894743911.html)
- GoCD: [Pipeline as Code](https://docs.gocd.io/17.4.0/advanced_usage/pipelines_as_code.html)
- ... and more

But these all have some downsides:

- These just work on the CI/CD server they were designed for
  - no cross-compability
- Inconvenient way of "programming" pipelines (as configuration files)
  - not very flexible
  - limited features
- These only work on the server side
  - locally developers can not make use of these
  - hard to test and debug

So why should a developer on his machine not make use of the pipeline on the server which has all the information about building, testing and running the code? After all (s)he uses most of the time the same commands and tools locally as on the server. This discrepancy can cause a "works on my machine" mindset and create confusion about different results when running on the server. In the worst case developer are not able to resolve the failing build because they can not reconstruct the differences between their local development stack and the one running on the server.

Lead to the rescue. It supports environment independent builds by running every task/job/step (or whatever you may call it) inside Docker containers. Hence no more version discrepancies for programming languages, build tools, os, etc. Every run of Lead is repeatable and returns the same result. You can run the same command locally and on the server and get the same result. 

This also encourages the DevOps mindset. Let's be honest, there is always this person in the project responsible for configuring the CI/CD server and/or pipeline. But as developers can and should make use of the pipeline script themselves, they can for the first time really and directly benefit of having a pipeline script.  and are enabled to adjust the pipeline -> creating again benefit for everybody else in the team.

It is also possible to use Lead with every CI/CD server imaginable. The only requirements are to be able to run Python and/or Docker (see [Installation](#Installation)). Ever switched your CI/CD server? It is very cumbersome and tedious. But having Lead as your pipeline tool you can easily use any CI/CD server without long configuration sessions or complete rewritings of your current pipeline. Now you can choose your CI/CD server solely by features like usability, design, feedback, performance, etc.

Lead is designed to give you all the power of a real programming language (Python <3) and a fully customizable virtual environment (Docker <3). Well, you deserve to see an example of a simple job to get the feeling:

```python
@job(description="Echoing Hello World.")
@docker("ubuntu:16.04")
def hello_world(exec):
  world_str="world".capitalize()
  exit_code, output = exec("""

    echo "Hello {world}!"

  """.format(world=world_str), shell="bash")
``` 
This example is very straightforward and just an appetizer. To learn more you can either start with [installing Lead](#Installation) or jump directly to [Getting Started](#GettingStarted) and even more [Examples](#Examples). If you have a question maybe it is already answered in the [FAQ section](#FAQ).

## Installation

### Prerequisites

You have to [install Docker](https://docs.docker.com/engine/installation/#supported-platforms). Lead was tested using Docker 17.03 Community Edition. But any newer version should work (even some older versions). If it does not work automatically try adjusting the settings described in the [Settings section](#Settings).

You also have to either [enable Docker management for non-root user](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (but be sure to read [Docker daemon attack surface](https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface) first) or have to run Lead every time with root privileges (e.g. executing with `sudo`).

### Using Docker

In the root directory of this project run

```bash
docker build -t lead .
```

to build a new Docker image containing everything necessary for running lead.

Create an alias for running the container using

```bash
alias lead="docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):/source -e CWD=$(pwd) -e HOME=$HOME lead"
```

Afterwards you can just execute `lead` followed by any command you wish.

### Using Python

Install Python 3 (at least 3.5). Install [docker-py](https://github.com/docker/docker-py#installation).

You can create a symlink for easy execution. For example:

```bash
ln -s <PATH_TO>/lead.py /usr/local/bin/lead
```

Or replace `/usr/local/bin` by another path inside your PATH-Variable.

## Settings

Having a Lead settings file is not necessary. But you can customize Lead using this file.

### Location

Lead looks in your home folder in `~/.lead/lead.settings.yml` for your configurations. If it does not exist just create it.

### Options

- `docker-api-version`
  - type: string
  - example: "1.27"
  - description: The API version of your installed Docker engine. Lead will try to automatically set the correct version. If this fails, you can get to know the real API version of your installation by executing `docker version` (without `--`) and set it using this option. You can find the value you need at "API version" under "server". 

### Example File

```yaml
- docker-api-version: "1.27"
```

## Getting Started

## CLI Commands

Basically you can run lead like this:

```bash
lead [<job> ...] [--<parameter>=<value> ...]
```

Where `<job>` is one (ore more) of the jobs of your pipeline script. And `<parameter>` and the according `<value>` are parameters your jobs will receive on execution[*](#Notes).

Make sure you are executing it from a directory containing a `pipeline.py` file.

```bash
lead [--info]
```
This will print all the available jobs and their meta information like descriptions.[*](#Notes)

```bash
lead <job> [<job> ...] [--dry-run]
```
This will run the pipeline using the `<job> [<job> ...]` as a starting point without actually executing the scripts inside the Docker containers. Instead it will print the complete pipeline by showing the jobs in execution order, their conditions and meta informations and the commands which could have been executed inside the Docker containers. This makes debugging easy and can be used as a communication tool to share, debug and discuss the pipeline.[*](#Notes)

## FAQ

- Do I have to use Docker for my project to use Lead?
  - No. You can use Lead to virtually create any deployment package you wish (e.g. .tar.gz, .rpm, .deb, etc.). But you have to install Docker to be able to run Lead.
- Does Lead take care of dependency management or compile my source code?
  - No, not directly. For dependency management, compilation etc. you still have to use tools like Maven, Composer, npm, etc. But Lead can run these tools for you and will help you using these in an reproducable environment. So instead of for example running `mvn clean package` and afterwards `tar -czf product.tar.gz target/*.jar` you can automate these steps using Lead and for example could just run `lead package` (given that you created a job named `package` inside your `pipeline.py` which does this).

# Warning Notice

This is just a **proof of concept** and executes your `pipeline.py` script without any safety checks or measures. So basically it is possible to do the same things a normal python script would be able to do.

For future versions of lead it is planned to restrict some functionalities of the pipeline script. But currently you have to make sure for yourself that you just use the functionalities provided by lead to avoid errors.

# Notes

\* Not yet implemented.