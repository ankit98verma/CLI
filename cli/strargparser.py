import inspect


# TODO: Comment the code
# TODO: Require an ability to give the inifinte argument with short and long form options

class CommandNotExecuted(Exception):

    def __init__(self, cmd_name):
        super().__init__(cmd_name + " not executed")
        self.cmd_name = cmd_name

    def __repr__(self):
        return "'" + self.cmd_name + "' command is not executed"


class WrongArgTpe(Exception):

    def __init__(self, wrong_arg_type, correct_arg_type):
        super().__init__('WrongArgTpe Exception:Cannot set the argument attributes. Correct argument type is: %s. '
                         'Attributes set for: %s' % (correct_arg_type, wrong_arg_type))


class IncompleteArg(Exception):

    def __init__(self, arg_details):
        super().__init__('IncompleteArg: Incomplete argument i.e. %s' % arg_details)


class AbsentArg(Exception):

    def __init__(self, absent_arg):
        super().__init__('AbsentArg Exception: Following argument is missing: \n\t%s' % str(absent_arg))


class InsufficientPosArgs(Exception):

    def __init__(self, req_arg_nos, provided_arg_nos):
        super().__init__('InsufficientPosArgs Exception: Insufficient number of positional arguments: Required: %d. '
                         'Provided %d' % (req_arg_nos, provided_arg_nos))


class InsufficientNargs(Exception):

    def __init__(self, arg, provided_val):
        super().__init__('InsufficientNargs Exception: Number of values for the argument with short form %s required '
                         'is: %d but provided %d values' % (str(arg.sh), arg.narg, provided_val))


class Arguments(dict):
    ARG_TYPES = {'POS': 0, 'INF': 1, 'COM': 2, 'OPT': 3}
    SH_INFO_TYPE = 'sh'
    LF_INFO_TYPE = 'lf'
    DES_INFO_TYPE = 'des'
    DT_INFO_TYPE = 'data_type'
    NARG_INFO_TYPE = 'narg'

    INT_DATA_TYPE = int
    BOOL_DATA_TYPE = bool
    FLOAT_DATA_TYPE = float
    STR_DATA_TYPE = str

    def __init__(self, arg_type):
        super().__init__()
        self.arg_type = arg_type
        self.sh = None
        self.lf = None
        self.des = None
        self.data_type = None
        self.narg = None

    def set_compulsory_attr(self, short_form, long_form, description, param_type, narg):
        if self.arg_type != Arguments.ARG_TYPES['COM']:
            raise WrongArgTpe
        self._set_attrs(short_form, long_form, description, param_type, narg)

    def set_optional_attr(self, short_form, long_form, description, param_type, narg):
        if self.arg_type != Arguments.ARG_TYPES['OPT']:
            raise WrongArgTpe
        self._set_attrs(short_form, long_form, description, param_type, narg)

    def set_positional_attr(self, position, description, param_type):
        if self.arg_type != Arguments.ARG_TYPES['POS']:
            raise WrongArgTpe
        short_form = str(position)
        long_form = short_form
        narg = 1

        self._set_attrs(short_form, long_form, description, param_type, narg)

    def set_infinity_attr(self, description, param_type):
        if self.arg_type != Arguments.ARG_TYPES['INF']:
            raise WrongArgTpe

        short_form = 'inf'
        long_form = '--infinity'
        narg = -1

        self._set_attrs(short_form, long_form, description, param_type, narg)

    def process_args(self, options):
        # convert to correct data type
        res = dict()
        res[self.sh] = []
        vals = options
        if self.data_type == bool:
            for v in vals:
                if v == 'true':
                    res[self.sh].append(True)
                elif v == 'false':
                    res[self.sh].append(False)
                else:
                    raise ValueError
        else:
            for v in vals:
                res[self.sh].append(self.data_type(v))

        return res

    def _set_attrs(self, short_form, long_form, description, param_type, narg):
        self.sh = short_form
        self.lf = long_form
        self.des = description
        self.data_type = param_type
        self.narg = narg

    def __repr__(self):
        string = ''
        string += self.sh + "\t" + str(self.data_type).replace('<class ', "").replace(">", "") + "\t" + self.lf + "\t" \
                  + self.des + ". No. of values required: " + str(self.narg) + "\n"
        return string

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value


class ArgumentManager:

    def __init__(self):

        self.pos_args = []
        self.inf_args = []
        self.com_args = []
        self.opt_args = []

    def add_comp_arg(self, short_form, long_form, description, param_type=str, narg=1):
        arg = Arguments(Arguments.ARG_TYPES['COM'])
        arg.set_compulsory_attr(short_form, long_form, description, param_type, narg)
        self.com_args.append(arg)

    def add_opt_arg(self, short_form, long_form, description, param_type=str, narg=1):
        arg = Arguments(Arguments.ARG_TYPES['OPT'])
        arg.set_optional_attr(short_form, long_form, description, param_type, narg)
        self.opt_args.append(arg)

    def add_inf_arg(self, description, param_type):
        if len(self.inf_args):
            print("Cannot add more than one infinity vars")
            return

        arg = Arguments(Arguments.ARG_TYPES['INF'])
        arg.set_infinity_attr(description, param_type)
        self.inf_args.append(arg)

    def add_pos_arg(self, description, param_type):
        arg = Arguments(Arguments.ARG_TYPES['POS'])
        arg.set_positional_attr(len(self.pos_args) + 1, description, param_type)
        self.pos_args.append(arg)

    def has_comp_args(self):
        return ArgumentManager._are_args(self.com_args)

    def has_opt_args(self):
        return ArgumentManager._are_args(self.opt_args)

    def has_inf_args(self):
        return ArgumentManager._are_args(self.inf_args)

    def has_pos_args(self):
        return ArgumentManager._are_args(self.pos_args)

    def get_comp_list(self, info_type):
        return ArgumentManager._get_list(self.com_args, info_type)

    def get_opt_list(self, info_type):
        return ArgumentManager._get_list(self.opt_args, info_type)

    def get_inf_list(self, info_type):
        return ArgumentManager._get_list(self.inf_args, info_type)

    def get_pos_list(self, info_type):
        return ArgumentManager._get_list(self.pos_args, info_type)

    def get_desc(self):
        string = ''
        if self.has_pos_args():
            string += "positional arguments (all compulsory):\n"
            for v in self.pos_args:
                string += "\t" + str(v)

        string += '\n'

        if self.has_comp_args():
            string += "compulsory arguments:\n"
            for v in self.com_args:
                string += "\t" + str(v)

        string += '\n'

        if self.has_opt_args():
            string += "optional arguments:\n"
            for v in self.opt_args:
                string += "\t" + str(v) + " "

        string += '\n'

        if self.has_inf_args():
            string += "infinite positional:\n"
            for v in self.inf_args:
                string += "\tType %s\n" % \
                          str(v.data_type).replace('<class ', "").replace(">", "")
            string += "\tare allowed"
        string += '\n'

        return string

    def standardize_args(self, options):
        # if -h is in the option then ignore all other arguments

        if '-h' in options:
            standard_args = ['-h']
            return standard_args

        standard_args = options.copy()

        if self.has_comp_args():
            # the compulsory arguments are present
            shs = self.get_comp_list(Arguments.SH_INFO_TYPE)
            lfs = self.get_comp_list(Arguments.LF_INFO_TYPE)
            # go through each element in the options and convert to sh if need be
            for i, e in enumerate(options):
                if e in lfs:
                    standard_args[i] = shs[lfs.index(e)]
            # All the compulsory options have been their short term forms

        if self.has_opt_args():
            # the compulsory arguments are present
            shs = self.get_opt_list(Arguments.SH_INFO_TYPE)
            lfs = self.get_opt_list(Arguments.LF_INFO_TYPE)
            # go through each element in the options and convert to sh if need be
            for i, e in enumerate(options):
                if e in lfs:
                    standard_args[i] = shs[lfs.index(e)]
            # All the optional options have been their short term forms

        return standard_args

    def build_bundle(self, std_opts):
        # bundle up the compulsory args

        res = dict()
        # ake care of compulsory arguments
        std_opts, res_tmp = self._bundle_comp_opt_args(std_opts, Arguments.ARG_TYPES['COM'])
        res.update(res_tmp)

        # now take care of optional arguments
        std_opts, res_tmp = self._bundle_comp_opt_args(std_opts, Arguments.ARG_TYPES['OPT'])
        res.update(res_tmp)

        # now take care of positional arguments
        std_opts, res_tmp = self._bundle_pos_args(std_opts)
        res.update(res_tmp)

        std_opts, res_tmp = self._bundle_inf_args(std_opts)
        res.update(res_tmp)

        return res

    def _bundle_comp_opt_args(self, std_opts, arg_type):
        shs = self.get_comp_list(Arguments.SH_INFO_TYPE)
        shs.extend(self.get_opt_list(Arguments.SH_INFO_TYPE))

        res = dict()
        if arg_type == Arguments.ARG_TYPES['COM']:
            arg_arr = self.com_args
            cond = self.has_comp_args()
        else:
            arg_arr = self.opt_args
            cond = self.has_opt_args()

        if cond:
            # go through each argument
            for a in arg_arr:
                if a.sh not in std_opts:
                    # missing a compulsory argument
                    if arg_type == Arguments.ARG_TYPES['COM']:
                        raise AbsentArg(a)
                    else:
                        continue
                op_ind = std_opts.index(a.sh)

                if (len(std_opts) - op_ind - 1) < a.narg:
                    raise InsufficientNargs(a, len(std_opts) - op_ind - 1)

                arg_vals = std_opts[op_ind + 1:op_ind + a.narg + 1]

                # check that the arg_vals don't contain any other args indicator (comp or optional)
                other_args_ind = sum([a in shs for a in arg_vals])
                if other_args_ind > 0:
                    raise InsufficientNargs(a, a.narg - other_args_ind)

                res.update(a.process_args(arg_vals))

                # now remove the data from the std_opts
                del (std_opts[op_ind:op_ind + a.narg + 1])

        return std_opts, res

    def _bundle_pos_args(self, std_opts):
        res = dict()
        if self.has_pos_args():
            if len(std_opts) < len(self.pos_args):
                raise InsufficientPosArgs(len(self.pos_args), len(std_opts))
            # we have sufficient number for arguments for positional arguments

            for p in self.pos_args:
                # go through each positional argument and get the results
                res.update(p.process_args(std_opts[0:p.narg]))

                del (std_opts[0:p.narg])
        return std_opts, res

    def _bundle_inf_args(self, std_opts):
        res = dict()
        if self.has_inf_args():
            p = self.inf_args[0]
            res.update(p.process_args(std_opts[0:]))

            for i in std_opts[0:p.narg]:
                std_opts.remove(i)

        return std_opts, res

    @staticmethod
    def _are_args(arg_list):
        return len(arg_list) > 0

    @staticmethod
    def _get_list(arg_list, info_type):
        arg_l = []
        for a in arg_list:
            arg_l.append(a[info_type])
        return arg_l

    def __repr__(self):
        string = ''
        if self.has_opt_args():
            for v in self.opt_args:
                string += " [" + v.sh + "]"

        if self.has_comp_args():
            for v in self.com_args:
                string += " " + v.sh

        if self.has_pos_args():
            for v in self.pos_args:
                string += " " + v.sh

        if self.has_inf_args():
            for v in self.inf_args:
                string += " " + v.des + "..."

        return string


class Command:

    def __init__(self, command_name, description, function):
        self.description = description
        self.command_name = command_name
        self._arg_manager = ArgumentManager()

        self.function = function

    def __repr__(self):
        string = "usage: " + self.command_name
        string += str(self._arg_manager)

        return string

    def set_function(self, function):
        self.function = function

    def show_help(self, out_func=print):
        string = self.__repr__()
        string += "\n\n"
        string += self.description + "\n"
        string += "\n"
        string += self._arg_manager.get_desc()
        out_func(string)

    def add_infinite_arg(self, description, param_type=str):
        self._arg_manager.add_inf_arg(description, param_type)

    def add_positional_argument(self, description, param_type=str):
        self._arg_manager.add_pos_arg(description, param_type)

    def add_optional_argument(self, short_form, long_form, description, narg=1, param_type=str):
        self._arg_manager.add_opt_arg(short_form, long_form, description, param_type, narg)

    def add_compulsory_argument(self, short_form, long_form, description, narg=1, param_type=str):
        self._arg_manager.add_comp_arg(short_form, long_form, description, param_type, narg)

    def decode_options(self, options):

        std_options = self._arg_manager.standardize_args(options)
        # hand the Absent argument error here
        if '-h' in std_options:
            bundle = {'-h': []}
            return bundle

        bundle = None
        try:
            bundle = self._arg_manager.build_bundle(std_options)
        except InsufficientNargs as e:
            print(e)
        except AbsentArg as e:
            print(e)
        except InsufficientPosArgs as e:
            print(e)
        except ValueError as e:
            print(e)

        return bundle


class StrArgParser:

    def write_file(self, line, end="\n"):
        self.f_tmp.write(str(line) + end)

    def __init__(self, description="", input_string=">> ", stripped_down=False):
        self.commands = dict()
        self.f_tmp = None
        self.description = description
        self.input_string = input_string
        self.is_loop = True

        self.add_command('exit', "Close the CLI interface", function=self.exit_program)
        if not stripped_down:
            self.default_cmd()

    def default_cmd(self):

        self.add_command('ls_cmd', 'Lists all the available command with usage', function=self._ls_cmd)
        self.get_command('ls_cmd').add_optional_argument('-v', '--verbose', "Give the output in detail", narg=0)

        self.add_command('help', 'Gives details of all the available commands', function=self._help)
        self.add_command('script', "Runs the script.", function=self._script)
        self.get_command('script').add_infinite_arg("The script files which is to be executed. They will be executed "
                                                    "in order they are provided")
        self.get_command('script').add_optional_argument('-v', '--verbose',
                                                         'Prints out the commands being executed from '
                                                         'the script', narg=0)

    def __repr__(self):
        return self.description

    def get_command(self, name):
        return self.commands[name]

    def add_command(self, command, description, function=None):
        c = Command(command, description, function)
        c.add_optional_argument('-h', '--help', 'Gives the details of the command', narg=0)
        c.add_optional_argument('->', '->', 'Overwrite the output to the file')
        c.add_optional_argument('->>', '->>', 'Append the output to the file')
        self.commands[command] = c

    def close_f_tmp(self):
        if self.f_tmp is not None:
            self.f_tmp.close()
            self.f_tmp = None

    @staticmethod
    def _get_options(input_str):

        single_q_index = [None]
        double_q_index = [None]

        single_q_strs = []
        double_q_strs = []

        single_q_p = 0
        double_q_p = 0

        for i, charac in enumerate(input_str):
            if charac == "'":
                if double_q_index[0] is not None:
                    continue
                if single_q_p == 0:
                    single_q_index[0] = i
                else:
                    single_q_strs.append(input_str[single_q_index[0] + 1:i])
                    single_q_index[0] = None
                single_q_p += 1
                single_q_p %= 2
            elif charac == '"':
                if single_q_index[0] is not None:
                    continue
                if double_q_p == 0:
                    double_q_index[0] = i
                else:
                    double_q_strs.append(input_str[double_q_index[0] + 1:i])
                    double_q_index[0] = None
                double_q_p += 1
                double_q_p %= 2

        if single_q_index[0] is not None:
            raise IncompleteArg("Single quote not closed.")
        if double_q_index[0] is not None:
            raise IncompleteArg("Double quote not closed.")

        single_q_strs.extend(double_q_strs)

        for s_inst in single_q_strs:
            s_inst_u = s_inst.replace(' ', '_')
            input_str = input_str.replace(s_inst, s_inst_u)

        # now split based on ' '
        opts = input_str.split(' ')
        for i, opts_inst in enumerate(opts):
            if "'" in opts_inst or '"' in opts_inst:
                opts[i] = opts_inst.strip('"').strip("'").replace('_', ' ')
            opts[i] = opts[i].strip(' ')

        return opts

    def decode_command(self, s):
        s = s.strip(' ')
        s = s.strip('\t')
        try:
            s = StrArgParser._get_options(s)
        except IncompleteArg as e:
            print(e)
            return None, None, None, print

        try:
            s.remove('')
        except ValueError:
            pass
        try:
            res = self.commands[s[0]].decode_options(s[1:])
            out_func = print

            if res is None:
                return None, None, None, print

            ls_key = list(res.keys())
            c = None
            if '->' in ls_key:
                c = '->w'
            elif '->>' in ls_key:
                c = '->>a'
            if c is not None:
                self.f_tmp = open(res[c[:-1]][0], c[-1])
                out_func = self.write_file
            if '-h' in ls_key:
                self.commands[s[0]].show_help(out_func=out_func)
                self.close_f_tmp()
                return None, None, None, None

            return s[0], res, self.commands[s[0]].function, out_func
        except KeyError:
            print("Command not found. Use 'help' command.")
            return None, None, None, print

    def exit_program(self):
        print("Exiting")
        self.is_loop = False
        return True

    def _ls_cmd(self, res, out_func=print):
        is_verbose = '-v' in list(res.keys())
        for k, v in self.commands.items():
            out_func("Command: " + k),
            if is_verbose:
                out_func(v)
                out_func("\n" + v.description + "\n\n\t\t---x---\n")

    def _help(self, out_func=print):
        for k, v in self.commands.items():
            out_func("Command " + k)
            v.show_help(out_func=out_func)
            out_func("\t\t----x----\n")
        self.close_f_tmp()

    def _script(self, res, out_func=print):
        exec_res = True
        stop_exec = False

        try:
            for files in res['inf']:
                i = 0
                f = open(files, 'r')
                for line in f:
                    i += 1
                    if line[0] == '#':
                        continue
                    line = line.replace('\t', '').strip(' ').strip('\n')
                    
                    if line != '':
                        if line[0] == '?':
                            if exec_res is False:
                                stop_exec = True
                                out_func("Error: Stopping the script because the command at line no. %d of script file '%s' "
                                         "return False" % (i-1, files))
                                break
                            continue
                            
                        if '-v' in res:
                            out_func(self.input_string + line)
                        try:
                            self.is_loop, exec_res = self.exec_cmd(line)
                        except CommandNotExecuted as e:
                            print(e)
                            stop_exec = True
                            break
                    if not self.is_loop:
                        break
                if not self.is_loop or stop_exec:
                    exec_res = False
                    break
        except FileNotFoundError:
            out_func('The file not found')
            raise CommandNotExecuted('script')
        except UnicodeDecodeError:
            out_func('The data_struct in the file is corrupted')
            raise CommandNotExecuted('script')

        return exec_res

    def run(self):
        self.is_loop = True
        while self.is_loop:
            s = input(self.input_string).strip(' ')
            if len(s) == 0:
                continue
            try:
                self.is_loop, _ = self.exec_cmd(s)
            except CommandNotExecuted as e:
                print(e)

    def exec_cmd(self, s):
        (cmd, res, func, out_func) = self.decode_command(s)
        exec_res = False
        if res is None:
            return self.is_loop, exec_res
        param_list = list(inspect.signature(func).parameters.keys())
        if 'res' in param_list and 'out_func' in param_list:
            exec_res = func(res, out_func=out_func)
        elif 'res' in param_list:
            exec_res = func(res)
        elif 'out_func' in param_list:
            exec_res = func(out_func=out_func)
        else:
            exec_res = func()

        self.close_f_tmp()

        if exec_res is None:
            exec_res = True

        return self.is_loop, exec_res
