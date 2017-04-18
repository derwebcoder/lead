import docker as d

client = d.from_env(version="1.27")
ll_client = d.APIClient(version="1.27")

def exec_wrapper(container):
    def exec(cmd):
        print("exec " + cmd + " in " + container.id)

        exec_id = ll_client.exec_create(container.id, cmd)['Id']
        exec_stream = ll_client.exec_start(exec_id, detach=False, stream=True)

        output = ""

        for line in exec_stream:
            print(line.decode('UTF-8'))
            output = output + line.decode('UTF-8')

        exec_result = ll_client.exec_inspect(exec_id)
        
        return exec_result['ExitCode'], output
    
    return exec

def docker(image):
    def docker_decorator(func):
        container = client.containers.run(image, "sleep infinity", detach=True)
        def func_wrapper(name):
            func(name, exec=exec_wrapper(container))
            container.kill()
            container.remove(force=True)
        return func_wrapper
    return docker_decorator


@docker("ubuntu")
def test(name, exec=None):
    print("test")
    exit_code, output = exec("bash -c 'echo '" + name + "'; echo 'Marian'; echo 'Franzi'; exit 6'")

    print("exit code is " + str(exit_code))
    print("Command output is: ")
    print(output)


test("Marvin")