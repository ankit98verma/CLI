from cli import strargparser as argp


def exit_prog(out_func):
    out_func("yeah! exiting")


def c1(res, out_func):
    out_func("C1:")
    out_func(res)



if __name__ == '__main__':

    par = argp.StrArgParser(description="Parser 1", ip_port=5000)
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

    # par.get_command('exit').set_function(exit_prog)

    # par.add_command('exit', "Close the CLI interface", function=exit_prog)
    # input_string = ">>"
    # loop = True
    # while loop:
    #     s = input(input_string).strip(' ')
    #     if len(s) == 0:
    #         continue
    #     try:
    #         loop = exec_cmd(s, par)
    #     except argp.CommandNotExecuted as e:
    #         print(e)

