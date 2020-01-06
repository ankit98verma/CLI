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
4. Go to the folder newly created folder "dist" and run following command
~~~
pip install CLI-1.0.0.tar.gz
~~~ 
OR
~~~
pip3 install CLI-1.0.0.tar.gz 
~~~

The package is installed, see the "Usage" section for some examples on setup.

## Usage


