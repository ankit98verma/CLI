from cli import strargparser as argp
from threading import RLock


def exit_prog(out_func):
    out_func("yeah! exiting")


def c1(res, out_func):
    out_func("C1:")
    out_func(res)



if __name__ == '__main__':
    rlck = RLock()

    par = argp.StrArgParser(description="Parser 1", ip_port=5000, rlocker=rlck, input_string="hello>> ")
    print(par)

    par.add_command('c1', "Command 1", function=c1)
    par.get_command('c1').add_infinite_arg('List of integers', int)
    par.get_command('c1').add_compulsory_argument('-f', '--file', "The file name", narg=argp.StrArgParser.INF)
    par.get_command('c1').add_compulsory_argument('-c', '--com', "The compulsory item name")
    # par.get_command('c1').add_optional_argument('-n', '--number', "A1 number", narg=1, param_type=int)
    # par.get_command('c1').add_optional_argument('-o', '--option', "An option", narg=0)

    # par.get_command('c1').add_positional_argument('First pos arg', param_type=int)
    # par.get_command('c1').add_positional_argument('Second pos arg', param_type=float)

    print(par.get_command('c1').show_help())

    par.run()



