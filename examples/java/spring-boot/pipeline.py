@job(description="Executing Maven to build the project.")
@docker(
    "maven:3.5.0-jdk-8-alpine",
    volumes=["~/.m2:/.m2:rw"])
def build(exec, *args, **kwargs):
    exec("""

        mvn clean package -Duser.home=/

    """, shell="sh")

@job(description="Stopping and removing old containers.")
@docker(
    "docker:17.03.1-ce-dind", 
    mountDaemon=True, 
    useHostUser=False)
def down(exec, *args, **kwargs):
    exec("""

        docker stop spring-example
        docker rm spring-example

    """, shell="sh")

@job(description="Starting a container running the application.")
@docker(
    "docker:17.03.1-ce-dind", 
    mountDaemon=True, 
    useHostUser=False)
def up(exec, *args, **kwargs):
    depends(build, ifFalse=fileExists(pattern="target/*.jar"))
    depends(down, ifTrue=isContainerRunningWithId(id="spring-example"))
    exec("""

        docker run -d --name spring-example -v """ + getcwd() + """:/usr/src/myapp -w /usr/src/myapp -p 8080:8080 java:8 java -jar ./target/gs-spring-boot-0.1.0.jar
    
    """, shell="sh")
