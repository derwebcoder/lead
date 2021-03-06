# The most basic example
@job(description="Echoing hello world.")
@docker("alpine:latest")
def hello_world(exec, *args, **kwargs):
    exec("""
        
            echo "Hello World! :)"

        """, shell="sh")




# This example shows how to use the return code of a container 
# and the output to do some post execution checks.
@job(description="Example of working with return code and log output.")
@docker("ubuntu:16.04")
def output_and_return(exec, *args, **kwargs):

    exit_code, output = exec("""

            echo "I am successfully running inside an ubuntu container"
            echo "Now this script exits with return code 9, but the build should not fail because of the output condition"
            exit 9

        """, shell="bash")
    
    # Enable the following code to let the pipeline fail
    # exit_code, output = exec("""
    #         echo "I am failing this build."; 
    #         exit 5
    #     """, shell="bash")
    
    print("Exit code is: " + str(exit_code))
    print("Command output is: ")
    print(output)

    if exit_code > 0:
        if "successfully" not in output:
            return exit_code
        else:
            return 0
    
    return 0




# This is an example for manipulating files
# Your current working directory is automatically mounted
# inside the container. So you have full access to it.
@job(description="Example of manipulating files inside the current working directory.")
@docker("ubuntu:16.04")
def alter_file(exec, *args, **kwargs):

    subj=nameToUpper("Susi") # See below for nameToUpper function
    verb=nameToUpper("eat")
    obj=nameToUpper("a hamburger")

    # This example uses locals() as a shortcut to make every variable 
    # of this function available inside the script
    # For a more specific way see the function complexLogic
    exec("""

            date +%d.%m.%Y > example.txt
            echo "This file has been created inside the container" >> example.txt
            echo "Today {subj} wants to {verb} {obj}." >> example.txt

        """.format(**locals()), shell="bash")




# This job shows an example of a more complex script inside a container
# Also the name of the job differs from the name given in @job
# Lead will prefer the name given in @job and fallback to the function name of
# none is specified in @job.
# Try changing "World" to something different and execute this job again to see this script really working
# You can also use command parameters. Try executing "lead helloAgain --name=Peter".
@job(name="helloAgain", description="Echoing hello to somebody.")
@docker("alpine:latest")
def complex_logic(exec, name="World", *args, **kwargs):

    name=nameToUpper(name) # See below for nameToUpper function

    exec("""

            if [ "{name}" = "WORLD" ]
                then
                    echo "Hello World!"
                else
                    echo "Not hello world but hello {name}."
            fi

        """.format(name=name), shell="sh")




# This is just a simple function and not directly executable by lead
# But extracting common tasks outside of jobs into its own functions
# can help organize the pipeline script
def nameToUpper(name=""):
    return name.upper()