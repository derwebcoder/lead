@job()
@docker("docker:17.03.1-ce-dind", mountDocker=True)
def clean(exec=None):
    # Cleaning target directory
    exec("""
    echo "cleaning ...";
    rm -rf target
    """, shell="sh")

@job()
@docker("maven:3.5.0-jdk-8-alpine")
def build(exec=None):
    clean()
    exec("""
    ls -l;\
    mvn package
    """, shell="sh")

@job()
@docker("docker:17.03.1-ce-dind", mountDocker=True)
def clean_docker(exec=None):
    # Removing old running containers
    exec("""
    docker stop spring-example &&
    docker rm spring-example
    """, shell="sh")

@job()
@docker("docker:17.03.1-ce-dind", mountDocker=True)
def up(exec=None):
    build()
    clean_docker()
    exec("""
    ls -l ;
    ls -l target ;
    docker run -d --name spring-example -v """ + os.getcwd() + """:/usr/src/myapp -w /usr/src/myapp -p 8080:8080 java:8 java -jar ./target/gs-spring-boot-0.1.0.jar
    """, shell="sh")
