# CLI
A package to add command line interface to any python program.
The package allows to add commands to the parser. Each command can have
compulsory arguments, optional arguments, positional arguments, countably
infinite arguments.

For example, following are the syntax of a command that have a 
compulsory argument (-c) and an optional argument (-o)
~~~ 
c1 -c 33 -o 22
c1 -c 33
~~~

## Installing the package
Steps to install the package
1. Clone or download the project.
2. Open command prompt and go to the folder containing the setup.py file
3. Run following command
~~~
python setup.py sdist
~~~ 
OR
~~~
python3 setup.py sdist
~~~
4. Go to the newly created folder "dist" and run following command
~~~
pip install CLI-x.x.x.tar.gz
~~~ 
OR
~~~
pip3 install CLI-x.x.x.tar.gz 
~~~

The package is installed, see the "Usage" section for some examples.

## Usage

### Simple CLI interface
In this section we will make a very simple CLI interface for out software.
It will have bare minimum commands and capabilities.

First import the package
```python
from cli import strargparser as argp
```
If you are using python2.7 then import the following package.
```python
from cli2_7 import strargparser as argp
```

Let us make an instance of parser. This parser have a description "Parser 1"
```python
parser = argp.StrArgParser(description="Parser 1")
```
Now let us start the CLI interface. The following function call is a **blocking** function
call. Hence it is advised to use thread in case program need to do other processings.
```python
parser.run()
```
So overall program is as follows:
```python
from cli import strargparser as argp

parser = argp.StrArgParser(description="Parser 1")
parser.run()
```
OR (for python2.7)

```python
from cli2_7 import strargparser as argp

parser = argp.StrArgParser(description="Parser 1")
parser.run()
```
Running the above program will lead to following console:
~~~
>>
~~~

By default the parser already have following commands built - in:
1. ls_cmd
2. exit
3. script
4. help

Let's find out what does 'ls_cmd' do, for which we will see the help of 'ls_cmd' command.
Try running following command:
~~~
>>ls_cmd -h
usage: ls_cmd [-h] [->] [->>] [-v]

Lists all the available command with usage

optional arguments with options:
	-h	'str'	--help	Gives the details of the command. No. of values required: 0
	->	'str'	->	Overwrite the output to the file. No. of values required: 1
	->>	'str'	->>	Append the output to the file. No. of values required: 1
	-v	'str'	--verbose	Give the output in detail. No. of values required: 0
~~~
So option '-h' or '--help' gives the details of the command.
So now let us run ls_cmd command:
~~~
>> ls_cmd
Command: exit
Command: ls_cmd
Command: help
Command: script
~~~

Go on and explore other commands! Remember '-h' or '--help' gives the explanation of the 
command
