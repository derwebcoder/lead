# Lead - Spring-Boot Example

This project is actually the project from the [spring-boot getting started guide](https://spring.io/guides/gs/spring-boot/).
The source code is from the `complete` folder of the repository you can find here (licensed also under the Apache License, Version 2.0): [https://github.com/spring-guides/gs-spring-boot](https://github.com/spring-guides/gs-spring-boot).
Only this `README.md` and the `pipeline.py` file were added.

## Running The Example

You can start the example application using `lead up`. This will build and test the application using Maven and start a container running the built `.jar` file.
You can verfiy this by executing `curl localhost:8080`.

If you try running `lead up` again, you will notice that Lead does not build the source again (but stopping the previously started container). This is because of Leads philosophy of having every job atomic (as long as the dependencies are given). You can and should trigger a new build by running each necessary job explicitly, for example by executing `lead build up`. Try to design your pipelines this way. It helps to make it transparent for the user what actually will be executed. And it makes it possible to run each job individually.

To stop and remove the running application you can use `lead down`.

## What It Does

This pipeline has three jobs:

- `build`
  - This job will execute Maven to test the code and build a `.jar` file. It adds an additional volume `~/.m2:/.m2:rw`. Basically it adds your personal Maven directory containing the Maven settings and local repository to your container in `read-write` mode. So the project dependendies will be saved outside of the container and it is not necessary to download all the dependencies everytime you run the pipeline.
  Note that it is necessary to set `-Duser.home=/` to the path where you added the volume for your Maven directory inside the container.
- `down`
  - This job will stop and remove previously started containers of the pipeline. The container will always be started by the job `up` with the name `spring-example`. This jobs uses two new parameters for `@docker`. `mountDaemon` will mount the Docker daemon inside your container. This is basically a shortcut for adding the volume `/var/run/docker.sock:/var/run/docker.sock:ro`. The second parameter is `useHostUser`. By default the commands inside the container will be run as your user. This makes it possible that altering files in your current working directory does not set the permissions to the root user. But to use the Docker daemon it is necessary to run as root. So instead of forcing to use the local user, the commands will be executed as root (or as whatever user is enabled by default inside the container).
- `up`
  - This job will start a new container, mounting the `.jar` file and execute it. It also introduces the new function `depends`. You can use this to define other jobs this job is dependent on. You can use either `isTrue` or `isFalse` or both together to decide whether it is really necessary to run it first. This example depends on `build`, but only if there is no `.jar` file. Also it depends on `down` to stop and remove previously started containers to avoid a naming conflict.

## Exercise

Try changing or adding the current pipeline to use Gradle instead of Maven. There is an official image for [Gradle](https://hub.docker.com/_/gradle/). All you have to execute is `gradle build`. And do not forget to change the path to the `.jar` file as Gradle is using a `build` folder instead of a `target` folder.