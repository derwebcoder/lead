@docker("ubuntu")
@job(name="ubuntu test", description="Does some magical stuff")
def test(name, age="6", exec=None):
    print("test")
    exit_code, output = exec("bash -c 'echo '" + name + "'; echo 'ist" + age + "'; echo 'Franzi'; exit 6'")

    print("exit code is " + str(exit_code))
    print("Command output is: ")
    print(output)