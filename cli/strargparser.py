import inspect
import socket
import os
from time import sleep
from threading import Thread
from threading import current_thread
import pickle as pk
import warnings


# TODO: Comment the code

__CONN__ = None


def _default_out(input_str):
    if __CONN__ is None:
        print(input_str)
    else:
        input_str = str(input_str)
        input_str += '\n'
        try:
            __CONN__.sendall(input_str.encode())
            __CONN__.sendall("".encode())
        except ConnectionError:
            print(input_str)
        except OSError:
            print(input_str)

class IllegalFunctionDefException(Exception):

    def __init__(self, func_str):
        super().__init__(func_str + " definition is Illegal")
        self.func_str = func_str

    def __repr__(self):
        return "'" + self.func_str + " definition is Illegal"

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


class Results(dict):

    def __init__(self):
        super().__init__()
    
    def get_argument(self, opt):
        return self[opt]

    def get_infinity_arguments(self):
        return self['inf']

    def get_positional_arguments(self, pos=None):
        if pos is not None:
            if pos <= 0:
                raise KeyError("Position value should be 1 or greater")
            pos = str(pos)
            return {pos: self[str(pos)]}
        else:
            res = {}
            for k, v in self.items():
                try:
                    int(k)
                    res.update({k: v})
                except ValueError:
                    pass
            return res
    
    def is_present(self, opt):
        return opt in self.keys()


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
        # string += self.sh + "\t" + str(self.data_type).replace('<class ', "").replace(">", "") + "\t" + self.lf + "\t" \
        #           + self.des + "\tNo. of values required: " + str(self.narg) + "\n"
        string += self.sh + "\t" + self.lf + "\t\t" +  str(self.data_type.__name__) + "\t" \
                  + self.des + "\tNo. of values required: " + str(self.narg) + "\n"
        
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
            raise ValueError("Cannot add more than one infinity vars")

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
            string += "\t\tare allowed"
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
            # the optional arguments are present
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

        # NOTE
        res = Results()
        # take care of compulsory arguments
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
                if a.narg == StrArgParser.INF:
                    # this has an infinite argument requirement. Find the next in the option list which is in shs list.
                    end_ind  = len(std_opts)
                    for i, p in enumerate(std_opts[op_ind+1:]):
                        if p in shs:
                            end_ind = op_ind + i + 1
                else:
                    end_ind = op_ind + a.narg + 1
                    if (len(std_opts) - op_ind - 1) < a.narg:
                        raise InsufficientNargs(a, len(std_opts) - op_ind - 1)
                if (end_ind == op_ind + 1) and arg_type == Arguments.ARG_TYPES['COM']:
                    raise InsufficientNargs(a, 0)
                
                arg_vals = std_opts[op_ind + 1:end_ind]
                
                # check that the arg_vals don't contain any other args indicator (comp or optional)
                other_args_ind = sum([a in shs for a in arg_vals])
                if other_args_ind > 0:
                    raise InsufficientNargs(a, a.narg - other_args_ind)

                res.update(a.process_args(arg_vals))

                # now remove the data from the std_opts
                del (std_opts[op_ind: end_ind])

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

        Command.verify_func_def(function)
        
        self.function = function

    def __repr__(self):
        string = "usage: " + self.command_name
        string += str(self._arg_manager)

        return string

    @staticmethod
    def verify_func_def(func):
        param_list = list(inspect.signature(func).parameters.keys())
        if len(param_list) > 4:
            raise IllegalFunctionDefException(str(func))

        if len(param_list) == 4:
            if 'res' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'res' parameter")
            if 'out_func' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'out_func' parameter")
            if 'out_func_err' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'out_func_err' parameter")
            if 'out_func_kwargs' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'out_func_kwargs' parameter")

        if len(param_list) == 3:
            if 'res' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'res' parameter")
            error = True
            if 'out_func' in param_list and  'out_func_err' in param_list:
                error = False
            if 'out_func' in param_list and  'out_func_kwargs' in param_list:
                error = False
            if 'out_func_err' in param_list and  'out_func_kwargs' in param_list:
                error = False
            if error:
                raise IllegalFunctionDefException(str(func) + " the paramters could be one of the following:  \n ['out_func', 'out_func_err'] \n ['out_func', 'out_func_kwargs'] \n ['out_func_err', 'out_func_kwargs']")

        if len(param_list) == 2:
            if 'res' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'res' parameter")
            
            error = True
            if 'out_func' in param_list:
                error = False
            if 'out_func_kwargs' in param_list:
                error = False
            if 'out_func_err' in param_list:
                error = False
            if error:
                raise IllegalFunctionDefException(str(func) + " the paramters could be one of the following:  \n 'out_func' \n 'out_func_kwargs' \n 'out_func_err'")
        else:
            # there is only one parameter
            if 'res' not in param_list:
                raise IllegalFunctionDefException(str(func) + " missing 'res' parameter")

    def set_function(self, function):
        Command.verify_func_def(function)
        self.function = function

    # def show_help(self, out_func=_default_out):
    def show_help(self, out_func, out_func_kwargs):
        string = self.__repr__()
        string += "\n\n"
        string += self.description + "\n"
        string += "\n"
        string += self._arg_manager.get_desc()
        out_func(string, **out_func_kwargs)

    def add_infinite_arg(self, description, param_type=str):
        warnings.filterwarnings("default", category=DeprecationWarning)
        warnings.warn("This method is deprecated. It will be removed in future versions. Please use 'add_infinite_argument' method instead.", DeprecationWarning)
        
        self._arg_manager.add_inf_arg(description, param_type)

    def add_infinite_argument(self, description, param_type=str):
        self._arg_manager.add_inf_arg(description, param_type)

    def add_positional_argument(self, description, param_type=str):
        self._arg_manager.add_pos_arg(description, param_type)

    def add_optional_argument(self, short_form, long_form, description, narg=1, param_type=str):
        self._arg_manager.add_opt_arg(short_form, long_form, description, param_type, narg)

    def add_compulsory_argument(self, short_form, long_form, description, narg=1, param_type=str):
        self._arg_manager.add_comp_arg(short_form, long_form, description, param_type, narg)

    def decode_options(self, options):

        std_options = self._arg_manager.standardize_args(options)
        
        if '-h' in std_options:
            bundle = {'-h': []}
            return bundle

       
        bundle = self._arg_manager.build_bundle(std_options)
        
        return bundle

class ThreadException(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class ParserThreadManager:

    def __init__(self, rlocker):
        self.threads = {}
        self.rlocker = rlocker
    
    def run_new_thread(self, name, func, args):
        if name in self.threads.keys():
            raise ThreadException("Thread %s already exists." % name)
        
        th = Thread(target=func, args=args, name=name)
        with self.rlocker:
            self.threads[name] = th
        th.start()
    
    def update_thread_list(self):
        names = list(self.threads.keys()).copy()
        for k in names:
            self.threads[k].join(1)
            if not self.threads[k].is_alive():
                with self.rlocker:
                    self.threads.pop(k)
    
    def stop_threads(self):
        while len(self.threads) != 0:
            names = list(self.threads.keys()).copy()
            for k in names:
                # TODO: May be use a variable for timeout
                self.threads[k].join(1)
                if not self.threads[k].is_alive():
                    with self.rlocker:
                        self.threads.pop(k)


class StrArgParser:

    INF = -1

    def write_file(self, line, end="\n", **kwargs):
        self.f_tmp.write(str(line) + end)

    def __init__(self, description="", input_string=">> ", stripped_down=False, ip='127.0.0.1', ip_port=None, rlocker=None, allow_net_admin=False, internal_lock=True):
        self.commands = dict()
        self.f_tmp = None
        self.description = description
        self.input_string = input_string
        self.is_loop = True
        self.is_conn_loop = ip_port is not None

        # TODO: use self.allow_net_admin variable
        self.allow_net_admin = allow_net_admin
        
        self.add_command('exit', "Close the CLI interface", function=self._exit_prog)
        self.add_command('input_string', "Prints the string displayed to user asking for the input.", function=self._input_string)
        if not stripped_down:
            self.default_cmd()
        
        self.ip = ip
        self.ip_port = ip_port
        self.rlocker = rlocker
        self.internal_lock = internal_lock and (self.rlocker is not None)
        if self.ip_port is not None:
            if self.rlocker is None:
                raise Exception("Provide a RLock when using networking")
            
            self.listen_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_soc.settimeout(0.2) # timeout for listening
            self.listen_soc.bind((self.ip, self.ip_port))
            self.listen_soc.listen(10)
        else:
            self.listen_soc = None
        
        self.th_manager = ParserThreadManager(self.rlocker)

        self.cstd_out = print
        self.cstd_err = print
        self.default_kwargs = {}

    def set_default_out(self, cstd_out, cstd_err, **default_kwargs):
        self.cstd_out = cstd_out
        self.cstd_err = cstd_err
        self.default_kwargs = default_kwargs
    
    def set_std_outs(self, cstd_out, cstd_err, **default_kwargs):
        self.cstd_out = cstd_out
        self.cstd_err = cstd_err
        self.default_kwargs = default_kwargs

    def get_cmd_list(self):
        return self.commands.keys()

    def default_cmd(self):

        self.add_command('ls_cmd', 'Lists all the available command with usage', function=self._ls_cmd)
        self.get_command('ls_cmd').add_optional_argument('-v', '--verbose', "Give the output in detail", narg=0)

        self.add_command('help', 'Gives details of all the available commands', function=self._help)
        self.add_command('script', "Runs the script.", function=self._script)
        self.get_command('script').add_infinite_argument("The script files which is to be executed. They will be executed "
                                                    "in order they are provided")
        self.get_command('script').add_optional_argument('-v', '--verbose',
                                                         '_default_out out the commands being executed from '
                                                         'the script', narg=0)

    def __repr__(self):
        return self.description

    def __getitem__(self, cmd_name):
        return self.get_command(cmd_name)

    def __setitem__(self, cmd_name:str, cmd_obj:Command):
        cmd_obj.add_optional_argument('-h', '--help', 'Gives the details of the command', narg=0)
        cmd_obj.add_optional_argument('->', '->', 'Overwrite the output to the file')
        cmd_obj.add_optional_argument('->>', '->>', 'Append the output to the file')
        
        self.commands[cmd_name] = cmd_obj

    def get_command(self, name):
        return self.commands[name]

    def add_command(self, command, description, function):
        # verify the function defintion
        c = Command(command, description, function)

        c.add_optional_argument('-h', '--help', 'Gives the details of the command', narg=0)
        c.add_optional_argument('->', '->', 'Overwrite the output to the file')
        c.add_optional_argument('->>', '->>', 'Append the output to the file')
        self.commands[command] = c

    def remove_command(self, command):
        self.commands.pop(command)
        
    def close_f_tmp(self):
        if self.f_tmp is not None:
            self.f_tmp.close()
            self.f_tmp = None

    def _preprocess_input(self, input_s):
        if input_s.split(' ')[0] in self.get_cmd_list():
            return input_s
        
        if os.path.isfile(input_s):
            input_s = "script -v " + input_s
            return input_s
        else:
            self.cstd_err(input_s + " is neither a command nor a script", **self.default_kwargs)
            raise CommandNotExecuted(input_s)

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
        replace_str = "\%\%S$S\%\%"
        for s_inst in single_q_strs:
            s_inst_u = s_inst.replace(' ', replace_str)
            input_str = input_str.replace(s_inst, s_inst_u)

        # now split based on ' '
        opts = input_str.split(' ')
        for i, opts_inst in enumerate(opts):
            if "'" in opts_inst or '"' in opts_inst:
                opts[i] = opts_inst.strip('"').strip("'").replace(replace_str, ' ')
            opts[i] = opts[i].strip(' ')

        return opts
    
    def get_input_string(self):
        return self.input_string

    def decode_command(self, s):
        s = s.strip(' ')
        s = s.strip('\t')
        try:
            s = StrArgParser._get_options(s)
        except IncompleteArg as e:
            self.cstd_err(e, **self.default_kwargs)
            return None, None, None, self.cstd_out, self.cstd_err

        try:
            s.remove('')
        except ValueError:
            pass
        try:
            try:
                res = self.commands[s[0]].decode_options(s[1:])
            except (InsufficientNargs, AbsentArg, InsufficientPosArgs, ValueError) as e:
                self.cstd_err(e, **self.default_kwargs)
                res = None

            out_func = self.cstd_out
            out_func_err = self.cstd_err

            if res is None:
                return None, None, None, self.cstd_out, self.cstd_err

            ls_key = list(res.keys())
            c = None
            if '->' in ls_key:
                c = '->w'
            elif '->>' in ls_key:
                c = '->>a'
            if c is not None:
                self.f_tmp = open(res[c[:-1]][0], c[-1])
                out_func = self.write_file
                out_func_err = self.write_file
            if '-h' in ls_key:
                self.commands[s[0]].show_help(out_func=out_func, out_func_kwargs=self.default_kwargs)
                self.close_f_tmp()
                return None, None, None, None, None

            return s[0], res, self.commands[s[0]].function, out_func, out_func_err
        except KeyError:
            self.cstd_err("Command not found. Use 'help' command.", **self.default_kwargs)
            return None, None, None, self.cstd_out

    def _exit_prog(self, res):        
        self.is_loop = False
        self.is_conn_loop = False
        self.cstd_out("Exited", **self.default_kwargs)

        return True

    def _input_string(self, res, out_func, out_func_kwargs):
        out_func(self.get_input_string(), **out_func_kwargs)

        return True

    def _ls_cmd(self, res, out_func, out_func_kwargs):
        is_verbose = '-v' in list(res.keys())
        for k, v in self.commands.items():
            out_func("Command: " + k, **out_func_kwargs)
            if is_verbose:
                out_func(v, **out_func_kwargs)
                out_func("\n" + v.description + "\n\n\t\t---x---\n", **out_func_kwargs)

    def _help(self, res, out_func, out_func_kwargs):
        for k, v in self.commands.items():
            out_func("Command " + k, **out_func_kwargs)
            v.show_help(out_func=out_func, out_func_kwargs=out_func_kwargs)
            out_func("\t\t----x----\n", **out_func_kwargs)
        self.close_f_tmp()

    def _script(self, res, out_func, out_func_kwargs):
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
                                         "return False" % (i-1, files), **out_func_kwargs)
                                break
                            continue
                            
                        if '-v' in res:
                            out_func(self.input_string + line, **out_func_kwargs)
                        try:
                            exec_res = self.exec_cmd(line)
                        except CommandNotExecuted as e:
                            exec_res = False
                            self.cstd_err(e, **self.default_kwargs)
                            # stop_exec = True
                            # break
                    if not self.is_loop:
                        break
                if not self.is_loop or stop_exec:
                    exec_res = False
                    break
        except FileNotFoundError as e:
            out_func('The file not found.', **out_func_kwargs)
            out_func(e, **out_func_kwargs)
            raise CommandNotExecuted('script')
        except UnicodeDecodeError:
            out_func('The data_struct in the file is corrupted', **out_func_kwargs)
            raise CommandNotExecuted('script')

        return exec_res
    
    def exec_cmd(self, s, _conn=None):
        s = s.strip(' ')
        if len(s) == 0:
            return True
        
        s = self._preprocess_input(s.strip(' '))

        global __CONN__
        if _conn is not None: 
            prev_CONN = __CONN__
            __CONN__ = _conn
        
        s = s.strip(' ')
        if len(s) == 0:
            return True

        (_, res, func, out_func, out_func_err) = self.decode_command(s)
        exec_res = False
        if res is None:
            return exec_res
        param_list = list(inspect.signature(func).parameters.keys())
        
        if self.internal_lock:
            # print("Acquiring the lock")
            self.rlocker.acquire()

        # add conn to the res before passing it to the func
        res['conn'] = _conn
        if 'res' in param_list:
            if 'out_func_err' in param_list and 'out_func' in param_list:
                if 'out_func_kwargs' in param_list:
                    exec_res = func(res, out_func=out_func, out_func_err=out_func_err, out_func_kwargs=self.default_kwargs)
                else:
                    exec_res = func(res, out_func=out_func, out_func_err=out_func_err)
            elif 'out_func' in param_list:
                if 'out_func_kwargs' in param_list:
                    exec_res = func(res, out_func=out_func, out_func_kwargs=self.default_kwargs)
                else:
                    exec_res = func(res, out_func=out_func)
            elif 'out_func_err' in param_list:
                if 'out_func_kwargs' in param_list:
                    exec_res = func(res, out_func_err=out_func_err, out_func_kwargs=self.default_kwargs)
                else:
                    exec_res = func(res, out_func_err=out_func_err)
            else:
                exec_res = func(res)
        else:
            raise Exception("Something went very wrong! Contact for support.")
        
        # if 'res' in param_list and 'out_func_err' in param_list and 'out_func_kwargs' in param_list:
        #     exec_res = func(res, out_func_err=out_func_err, out_func_kwargs=self.default_kwargs)
        # if 'res' in param_list and 'out_func' in param_list and 'out_func_kwargs' in param_list:
        #     exec_res = func(res, out_func=out_func, out_func_kwargs=self.default_kwargs)
        # elif 'res' in param_list and 'out_func' in param_list:
        #     exec_res = func(res, out_func=out_func)
        # elif 'res' in param_list:
        #     exec_res = func(res)
        # else:
        #     # this should never happen because we are verifying the function definition
        #     raise Exception("Something went very wrong! Contact for support.")

        self.close_f_tmp()

        if _conn is not None:
            __CONN__ = prev_CONN
        
        if self.internal_lock:
            # print("Releasing the lock")
            self.rlocker.release()

        if exec_res is None:
            exec_res = True

        return exec_res

    def _get_conn(self, listen_soc):
        self.cstd_out("Waiting for the connection...", **self.default_kwargs)
        i = 0
        while self.is_conn_loop:
            try:
                _conn, addr = listen_soc.accept()
                # print("Connected to %s" % str(addr))
                self.th_manager.run_new_thread('Conn_%d:%s' % (i, addr[0]), self._accept_network_cmd, (_conn, addr, ))
                i += 1
            except socket.timeout:
                pass
        
        self.cstd_out("Stopped listening for connections...", **self.default_kwargs)
        
        listen_soc.close()
    
    def _accept_network_cmd(self, _conn, _addr):
        try:
            data = _conn.recv(5120)
        except OSError:
            pass
        
        if data:
            s = pk.loads(data)
            try:
                print(("{%s}" % current_thread().name)  + self.input_string + s)
                self.exec_cmd(s, _conn=_conn)
            except CommandNotExecuted as e:
                self.cstd_err(e, **self.default_kwargs)
        
        # close the connetion now
        _conn.close()
    
    def _accept_local_cmd(self, script):
        # if script is not None:
        #     try:
        #         self.exec_cmd('script -v %s' % script)
        #     except CommandNotExecuted as e:
        #         self.cstd_err(e, **self.default_kwargs)
        
        while self.is_loop:    
            s = input(self.input_string)
            try:
                self.exec_cmd(s)
            except CommandNotExecuted as e:
                self.cstd_err(e, **self.default_kwargs)
    
    def run(self, local_script=None):
        self.is_loop = True
        
        if self.ip_port is not None:
            # start the listening over a separate thread with _get_conn
            self.th_manager.run_new_thread("NetCMD", self._get_conn, args=(self.listen_soc,))
            
            # create a thread for local command accept
            self.th_manager.run_new_thread("LocalCMD", self._accept_local_cmd, args=(local_script, ))

            # start the threads management
            while self.is_loop:
                self.th_manager.update_thread_list()
        else:
            self._accept_local_cmd(local_script)
        
        # print("Joining the threads")
        self.th_manager.stop_threads()


class StrArgParserClient:

    def __init__(self):

        self.parser = StrArgParser("Client side parser")

        self.setup_cmds()

    def run(self):
        self.parser.run()

    def setup_cmds(self):
        self.parser.add_command('connect', "Connect to a server", self._connect)
        self.parser.get_command('connect').add_positional_argument('The IP address of the server')
        self.parser.get_command('connect').add_positional_argument('The port to connect to', param_type=int)
        self.parser.get_command('connect').add_optional_argument('-rn', '--Retry_Nos', 'Number of times to retry to connect. Give -1 for inifinitly. '
                                                                                        'Default is 5 times with delay of 1 second.', narg=1, param_type=int)

    def _transact_cmd(self, conn_soc,  s, out_func=None):
        
        if conn_soc is None:
            return

        conn_soc.sendall(pk.dumps(s))
        data = b''
        while True:
            try:
                data_tmp = conn_soc.recv(1024)
            except OSError:
                break
            data += data_tmp
            if not data_tmp:
                break
        try:
            rec_data = data.decode()
        except:
            rec_data = pk.loads(data)
            
        if out_func is not None:
            out_func(rec_data)
        conn_soc.close()

        return rec_data

    def _connect_utility(self, res, out_func):
        conn_soc  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn_soc.settimeout(1)
        retry_nos = 5
        if '-rn' in res.keys():
            retry_nos = res['-rn'][0]
        while retry_nos != 0:
            retry_nos -= 1
            try:
                conn_soc.connect((res['1'][0], res['2'][0]))
                
                # set the timeout to None
                conn_soc.settimeout(None)
                return conn_soc
            except ConnectionRefusedError:
                out_func("Connection Refused. Trying again")
            except ConnectionAbortedError:
                out_func("Connection Aborted. Trying again")
            except socket.timeout:
                out_func("Timeout. Trying again")
            sleep(1)
            
        
        return None

    def _connect(self, res, out_func):
        
        out_func('Trying to connect to %s at port %s' % (res['1'][0], res['2'][0]))

        conn_soc  = self._connect_utility(res, out_func)

        if conn_soc is None:
            out_func("Error: Cannot connect to %s at port %s" % (res['1'][0], res['2'][0]))
            return False
        
        input_str = self._transact_cmd(conn_soc, 'input_string')
        input_str = input_str.replace('\n', '')
        input_str = input_str.replace('>>', '')
        input_str = input_str.replace('$', '')
        input_str = input_str.replace(':', '')
        input_str = input_str.strip(' ')

        out_func("Connected!")
        
        go_next = True
        s = ''
        while go_next:
            s = input("(%s) >> " % input_str)
            s = s.strip(' ')
            if s == '':
                continue
            
            if s == 'disconnect':
                break
            
            if s == 'exit':
                s_tmp = ''
                while s_tmp != 'y' and s_tmp != 'n':
                    s_tmp = input ("Closing the Server. Are you sure?(y/n):")
                    if s_tmp == 'n':
                        break
                    elif s_tmp == 'y':
                        conn_soc  = self._connect_utility(res, out_func)
                        self._transact_cmd(conn_soc, s, out_func)
                        go_next = False   
            else:
                conn_soc  = self._connect_utility(res, out_func)
                self._transact_cmd(conn_soc, s, out_func)
        
        return True
            
