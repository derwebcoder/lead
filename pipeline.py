@job(name="ubuntu_test", description="Does some magical stuff")
@docker("ubuntu")
def test(name="marvin", age="6", exec=None):
    print("test")
    print(name)
    print(age)
    print(exec)
    exit_code, output = exec("bash -c 'echo 'Marvin'; echo 'ist6'; echo 'Franzi'; exit 6'")

    print("exit code is " + str(exit_code))
    print("Command output is: ")
    print(output)

@job(description="Does some magical stuff too")
@docker("ubuntu")
def testEinsZweiDrei(exec=None):
    exit_code, output = exec("bash -c 'echo \'ThisShitRocks\'; exit 0'")

@job(name="alterFile", description="Does some magical stuff too")
@docker("ubuntu")
def alterFile(exec=None):
    exit_code, output = exec("""
        echo "Eine Neue Zeile" >> test.txt &&
        test=$(expr 3 + 4) ;
        echo "Das Ergebnis ist $test"
        """, shell="bash")