# 
@job(description="Example of working with return code and log output.")
@docker("ubuntu:16.04")
def output_and_return(exec=None):
    exit_code, output = exec("""
            echo "I'm successfully running inside an ubuntu container";
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



# This job shows an example of a more complex script inside a container
# Also the name of the job differs from the name given in @job
# Lead will prefer the name given in @job and fallback to the function name of
# none is specified in @job.
# Try changing the name and execute this job again to see this script really working
@job(name="helloWorld", description="Echoing the well known hello world.")
@docker("alpine")
def complexLogic(exec=None):
    name=nameToUpper("World")
    exec("""
            if [ "{name}" = "WORLD" ]
                then
                    echo "Hello World!"
                else
                    echo "Not hello world but hello {name}"
            fi
        """.format(name=name), shell="sh")

@job(description="Example of manipulating files inside the current working directory.")
@docker("ubuntu:16.04")
def alterFile(exec=None):
    subj=nameToUpper("Susi")
    verb=nameToUpper("eat")
    obj=nameToUpper("a hamburger")
    # This example uses locals() as a shortcut to make every variable 
    # of this function available inside the script
    # For a more specific way see the function complexLogic
    exec("""
            date +%d.%m.%Y > example.txt;
            echo "This file has been created inside the container" >> example.txt;
            echo "Today {subj} wants to {verb} {obj}." >> example.txt;
        """.format(**locals()), shell="bash")

# This is just a simple function and not directly executable by lead
# But extracting common tasks outside of jobs into its own functions
# can help organize the pipeline script
def nameToUpper(name=""):
    return name.upper()