# Lead - Getting Started

This example shows the basics and possibilities of Lead. It does not include a real project, just a simple pipeline.py file.

## Hello World

First of all the obvious example. Just printing "Hello World" to the logs.

Start by changing to the directory of this example. Execute the following line:

```bash
lead hello_world
```

This should print something like the following log:

```bash
==============================

INFO | Running hello_world

==============================


*** CONTAINER OUTPUT

Hello World! :)

*** END OF OUTPUT

==============================

Pipeline ended succesfully. :)

==============================
```

And this is what happened:

Take a look inside the `pipeline.py` file. The first job you will find has the function name `hello_world`. This is the function that has been executed. Defining a job in lead is as simple as creating a function in Python. You will get a variable called `exec`. This is a helper you can use to define what should happen inside the container. You also get something called `*args` and `**kwargs`. These are some kind of placeholders in Python for more parameters a function can receive but which are not explicitly mentioned in the parameter list. You can ignore them for now.

The magic happens in the two lines before the definition of the function. The decorator `@job` tells Lead that this function is actually a job you can execute from the command line. This is also the place you can enter more meta information about this job. Then there is the `@docker` decorator. We are using this decorator to tell Lead more about the container we want to use inside our job. For now the only thing to define is the image name - `alpine` - for this job.

So Lead will check if there is already an image called `alpine` on your machine. If not it will download the image. After that it will start a container of this image and give the helper function `exec` to your function to execute something inside the container. It will do even more for you automatically in the background, like mounting the current working directory inside the container, removing the container after execution of your job and so on.

You can use `exec` by first providing the script to execute inside your container and optionally a shell this should be executed in. In Python we can use a string starting with triple `"` which enables us to write the script in several lines and to use `"` inside it without having to escape them. Try changing the script and run the command again. You can also enter a `ls` to see the files of the current directory (probably `README.md` and `pipeline.py`) in the log.

## Container Output And Return Codes

This is example will show you how to get access to and use the output of the container and the return code.

The `exec` function will return two values: `exit_code` and `output`. The `exit_code` is the real exit code of the execution inside the container. `output` will contain the complete output of your script in one string.

Execute the following command.

```bash
lead output_and_return
```

You will get something like the following output.

```bash
==============================

INFO | Running output_and_return

==============================


*** CONTAINER OUTPUT

I am successfully running inside an ubuntu container
Now this script exits with return code 9, but the build should not fail because of the output condition

*** END OF OUTPUT
Exit code is: 9
Command output is: 
I am successfully running inside an ubuntu container
Now this script exits with return code 9, but the build should not fail because of the output condition


==============================

Pipeline ended succesfully. :)

==============================
```

We see the exit code was 9. This was intended and caused by `exit 9` inside the script. But why did Lead tell us that the `Pipeline ended successfully. :)`? Because there is a second condition inside the job which checks if there was a specific keyword in the output. In this case `successfully`. This is true, because we echoed this word inside our script.

Enable the commented lines and disable the first execution of `exec`. Run the command `lead output_and_return` again. Now the pipeline fails because there is no keyword `successfully` anymore. Lead will also fail with the exit code of the job. You can verify this by running `echo $?` in your command line.

## Manipulating Files

As previously mentioned the current working directory is mounted as a volume inside the container. You have full access to the files. It is possible to read, write, copy, move, remove, and so on. This enables us to run something like Maven, Grunt, etc. But for this example we will just create a new file called `example.txt` inside our current directory.

Run 

```bash
lead alter_file
```

You will see nothing special in the output. That's because we echoed everything inside the `example.txt`. Look in the current directory and you will find this exact file. It should container the current date, a new line of text and a third line with `Today SUSI wants to EAT A HAMBURGER.` If you look inside the job you will see that the corresponding line looks like this:

```bash
echo "Today {subj} wants to {verb} {obj}." >> example.txt;
```

Python replaces the placeholders because of the `format(**locals())` function we appended to the script string. The function `locals()` does contain all local variables of the current context in Python. So in this case the three previously defined variables `subj`, `verb` and `obj`. The `**` are just Pythons way of spreading these, so `format()` can use them. The equivalent but longer version would be to set them explicitly like this: `format(subj=subj, verb=verb, obj=obj)`.

By the way, for these three variables a function is used which you will find at the end of the `pipeline.py` file. This is not a job function but can be used as a helper function for typical or repeating tasks. These normal kind of functions will help you organize your pipeline and keep it readable.

## More Logic And Command Line Parameter

In the last example there is a more complex script containing a conditional statement. Execute the following command.

```bash
lead helloAgain
```

You will see something like the following output:

```bash
==============================

INFO | Running helloAgain

==============================


*** CONTAINER OUTPUT

Hello World!

*** END OF OUTPUT

==============================

Pipeline ended successfully. :)

==============================
```

You may wonder why you had to execute `lead helloAgain` and not something like `lead complex_logic`. This is because of the `@job` decorator and more specifically of the `name` given there. Lead prefers a job name given there and use the real function name as a fallback.

Execute the command again but add a parameter called `name`:

```bash
lead helloAgain --name=Jason
```

This time the output should look like this:

```bash
==============================

INFO | Running helloAgain

==============================


*** CONTAINER OUTPUT

Not hello world but hello JASON.

*** END OF OUTPUT

==============================

Pipeline ended successfully. :)

==============================
```

You see that the output has changed. It does contain the name entered on the command line.

If you look closely to the function header you will see a new parameter called `name`. This is the parameter we added to the command line. The value `World` is just a default value if no parameter is given. 

But the different output also shows us that you can use even use complex logic inside your container script. So basically there is no limitation of what you can do.