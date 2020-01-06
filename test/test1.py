from cli import strargparser as argp
import inspect


def exit_prog(out_func):
    out_func("exiting")


def c1(res):
    print("C1:")
    print(res)


def exec_cmd(s, parser):
    (cmd, res, func, out_func) = parser.decode_command(s)
    if res is None:
        return True
    param_list = list(inspect.signature(func).parameters.keys())
    if 'res' in param_list and 'out_func' in param_list:
        func(res, out_func=out_func)
    elif 'res' in param_list:
        func(res)
    elif 'out_func' in param_list:
        func(out_func=out_func)
    else:
        func()

    if cmd == 'exit':
        return False
    return True


if __name__ == '__main__':

    par = argp.StrArgParser("Parser 1")
    print(par)

    par.add_command('c1', "Command 1", function=c1)
    par.get_command('c1').add_infinite_args(int)
    par.get_command('c1').add_compulsory_arguments('-f', '--file', "The file name", narg=2)
    par.get_command('c1').add_compulsory_arguments('-c', '--com', "The compulsory item name")
    par.get_command('c1').add_optional_arguments('-n', '--number', "A number", narg=-1, param_type=int)
    par.get_command('c1').add_optional_arguments('-o', '--option', "An option", narg=0)
    par.get_command('c1').add_positional_arguments('First pos arg', param_type=int)
    par.get_command('c1').add_positional_arguments('Second pos arg', param_type=float)

    par.add_command('exit', "Close the CLI interface", function=exit_prog)
    par.run()
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

