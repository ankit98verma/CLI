
class CommandNotExecuted(Exception):

    def __init__(self, cmd_name):
        super().__init__(cmd_name+" not executed")
        self.cmd_name = cmd_name

    def __repr__(self):
        return "'"+self.cmd_name+"' command is not executed"


class Command:

    def __init__(self, command_name, description, inf_positional, function):
        self.description = description
        self.command_name = command_name
        self.positional_arguments = dict()
        self.compulsory_arguments = dict()
        self.optional_arguments = dict()
        self.function = function

        self.inf_positional = inf_positional
        self.inf_type = None
        self.has_positional = False
        self.has_optional = True
        self.has_compulsory = False

    def __repr__(self):
        string = "usage: " + self.command_name
        if self.has_optional:
            for v in self.optional_arguments.values():
                string += " [" + v['sh'] + "]"

        if self.has_compulsory:
            for v in self.compulsory_arguments.values():
                string += " "+v['sh']

        if self.has_positional:
            for v in self.positional_arguments.values():
                string += " "+v['sh']
        if self.inf_positional:
            string += " ..."

        return string

    def show_help(self, out_func=print):
        string = self.__repr__()
        string += "\n\n"
        string += self.description + "\n"
        string += "\n"
        if self.has_positional:
            string += "positional arguments (all compulsory):\n"
            for v in self.positional_arguments.values():
                string += "\t" + v['sh'] + "\t" + str(v['type']).replace('<class ', "").replace(">", "") + "\t" + v[
                    'lf'] + "\t" + v['des'] + "\n"

        if self.has_compulsory:
            string += "compulsory arguments with options:\n"
            for v in self.compulsory_arguments.values():
                string += "\t" + v['sh'] + "\t" + str(v['type']).replace('<class ', "").replace(">", "") + "\t" + v[
                    'lf'] + "\t" + v['des'] + ". No. of values required: "+str(v['narg']) + "\n"

        if self.has_optional:
            string += "optional arguments with options:\n"
            for v in self.optional_arguments.values():
                string += "\t" + v['sh'] + "\t" + str(v['type']).replace('<class ', "").replace(">", "") + "\t" + v[
                    'lf'] + "\t" + v['des'] + ". No. of values required: "+str(v['narg']) + "\n"
        if self.inf_positional:
            string += "Infinite positional parameters of type %s are allowed\n" % \
                      str(self.inf_type).replace('<class ', "").replace(">", "")

        out_func(string)

    def add_infinite_args(self, inf_type):
        self.inf_positional = True
        self.inf_type = inf_type

    def remove_infinite_args(self):
        self.inf_positional = False
        self.inf_type = None

    def add_positional_arguments(self, description, param_type=str):
        self.has_positional = True
        position = len(self.positional_arguments.keys()) + 1
        short_form = str(position)
        long_form = short_form
        narg = 1
        self.positional_arguments[position] = dict()
        self.positional_arguments[position]['sh'] = short_form
        self.positional_arguments[position]['lf'] = long_form
        self.positional_arguments[position]['des'] = description
        self.positional_arguments[position]['type'] = param_type
        self.positional_arguments[position]['narg'] = narg

    def add_optional_arguments(self, short_form, long_form, description, narg=1, param_type=str):
        self.has_optional = True
        self.optional_arguments[short_form] = dict()
        self.optional_arguments[short_form]['sh'] = short_form
        self.optional_arguments[short_form]['lf'] = long_form
        self.optional_arguments[short_form]['des'] = description
        self.optional_arguments[short_form]['type'] = param_type
        self.optional_arguments[short_form]['narg'] = narg

    def add_compulsory_arguments(self, short_form, long_form, description, narg=1, param_type=str):
        self.has_compulsory = True
        self.compulsory_arguments[short_form] = dict()
        self.compulsory_arguments[short_form]['sh'] = short_form
        self.compulsory_arguments[short_form]['lf'] = long_form
        self.compulsory_arguments[short_form]['des'] = description
        self.compulsory_arguments[short_form]['type'] = param_type
        self.compulsory_arguments[short_form]['narg'] = narg

    def get_sh_list(self):
        com_sh = list(self.compulsory_arguments.keys())
        opt_sh = list(self.optional_arguments.keys())
        com_sh.extend(opt_sh)
        return com_sh

    def get_lf_list(self):
        com_vals = list(self.compulsory_arguments.values())
        com_lf = []
        for i in com_vals:
            com_lf.append(i['lf'])
        opt_vals = list(self.optional_arguments.values())
        opt_lf = []
        for i in opt_vals:
            opt_lf.append(i['lf'])
        com_lf.extend(opt_lf)
        return com_lf

    def standardize(self, options):
        shs = self.get_sh_list()
        lfs = self.get_lf_list()

        options2 = options.copy()
        i = 0
        for o in options:
            if o in lfs:
                ind = lfs.index(o)
                options2[i] = shs[ind]
            i += 1
        return options2

    def bundle_data(self, options):
        bundle = dict()
        current_key = ""
        shs = self.get_sh_list()
        options_c = options.copy()
        for o in options:
            if '-' in o:
                current_key = o
                options_c.remove(current_key)
                if current_key in shs and current_key not in list(bundle.keys()):
                    bundle[current_key] = []
            else:
                if current_key in shs:
                    bundle[current_key].append(o)
                    options_c.remove(o)
        bundle[current_key].extend(options_c)
        return bundle

    def convert_type(self, vals, type):
        res = []
        if type == bool:
            for v in vals:
                if v == 'true':
                    res.append(True)
                elif v == 'false':
                    res.append(False)
                else:
                    raise ValueError
        else:
            for v in vals:
                res.append(type(v))
        return res

    def process_bundle(self, bundle):
        res_bundle = bundle.copy()
        pos_str = 'pos'
        inf_str = 'inf'
        res_bundle[pos_str] = []
        res_bundle[inf_str] = []
        got_args = list(bundle.keys())

        # first check if -h is in arguments
        if '-h' in got_args:
            return bundle
        # now check if all the compulsory arguments are present
        com_shs = list(self.compulsory_arguments.keys())
        res = all(ele in got_args for ele in com_shs)
        if not res:
            print("All compulsory arguments are not present")
            return None

        # now we got all the compulsory arguments, along with optional, and/or positional arguments and/or infinite args
        # positional and infinite arguments (if present) are mixed up in the compulsory and optional arguments
        rem_pos_count = len(self.positional_arguments.keys())
        for k, v in bundle.items():
            if k in com_shs:
                processing_dict = self.compulsory_arguments[k]
            else:
                processing_dict = self.optional_arguments[k]
            if processing_dict['narg'] == -1:
                extra_arg_len = 0
            else:
                extra_arg_len = len(v) - processing_dict['narg']
            if extra_arg_len > 0:
                # there are either some/all positional arguments or some extra arguments are given or infinite arguments
                if rem_pos_count > 0:
                    # there are some positional arguments
                    res_bundle[k] = v[:processing_dict['narg']]
                    if rem_pos_count - extra_arg_len >= 0:
                        rem_pos_count -= extra_arg_len
                        res_bundle[pos_str].extend(v[processing_dict['narg']:])
                    elif self.inf_positional:
                        res_bundle[pos_str].extend(v[processing_dict['narg']:][:rem_pos_count])
                        res_bundle[inf_str].extend(v[processing_dict['narg']:][rem_pos_count:])
                        rem_pos_count = 0
                    else:
                        print("More than required no. of values are given for argument: %s" % k)
                        return None
                else:
                    if self.inf_positional:
                        # there are some infinite arguments
                        res_bundle[k] = v[:processing_dict['narg']]
                        res_bundle[inf_str].extend(v[processing_dict['narg']:])
                        continue
                    else:
                        print("More than required no. of values are given for argument: %s" % k)
                        return None
            elif extra_arg_len < 0:
                print("For argument: %s. \n\tRequired no. of value is: %d  \n\tGiven number of value is: %s"
                      % (k, processing_dict['narg'], len(v)))
                print("\nLess number of values are given for %s" % k)
                return None
            try:
                res_bundle[k] = self.convert_type(res_bundle[k].copy(), processing_dict['type'])
            except ValueError:
                print("Wrong value is given for argument %s" % k)
                return None

        if rem_pos_count > 0:
            print("All positional arguments are not found")
            return None
        ii = 1
        res_list = []
        for v in res_bundle[pos_str]:
            try:
                res_list.extend(self.convert_type([v], self.positional_arguments[ii]['type']))
            except ValueError:
                print("Wrong value is given for argument %s" % v)
                return None
            ii += 1
        res_bundle[pos_str] = res_list

        try:
            res_bundle[inf_str] = self.convert_type(res_bundle[inf_str].copy(), self.inf_type)
        except ValueError:
            print("Wrong value is given for infinite arguments")
            return None

        return res_bundle

    def decode_options(self, options):

        options = self.standardize(options)
        bundle = self.bundle_data(options.copy())
        proc = self.process_bundle(bundle)

        return proc


class StrArgParser:

    def write_file(self, line, end="\n"):
        self.f_tmp.write(str(line)+end)

    def __init__(self, description=""):
        self.commands = dict()
        self.f_tmp = None
        self.description = description

        self.add_command('ls_cmd', 'Lists all the available command with usage', function=self.cmd_ls_cmd)
        self.get_command('ls_cmd').add_optional_arguments('-v', '--verbose', "Give the output in detail", narg=0)

    def __repr__(self):
        return self.description

    def get_command(self, name):
        return self.commands[name]

    def add_command(self, command, description, inf_positional=False, function=None):
        c = Command(command, description, inf_positional, function)
        c.add_optional_arguments('-h', '--help', 'Gives the details of the command', narg=0)
        c.add_optional_arguments('->', '->', 'Overwrite the output to the file')
        c.add_optional_arguments('->>', '->>', 'Append the output to the file')
        self.commands[command] = c

    def cmd_ls_cmd(self, res, out_func=print):
        is_verbose = len(res) > 0
        for k, v in self.commands.items():
            out_func("Command: " + k),
            if is_verbose:
                out_func(v)
                out_func("\n"+v.description+"\n\n\t\t---x---\n")

    def show_help(self, res, out_func=print):
        for k, v in self.commands.items():
            out_func("Command "+k)
            v.show_help(out_func=out_func)
            out_func("\t\t----x----\n")

    def decode_command(self, s):
        s = s.strip(' ')
        s = s.strip('\t')
        s = s.split(' ')
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
            if '->' in ls_key:
                self.f_tmp = open(res['->'][0], 'w')
                out_func = self.write_file
            elif '->>' in ls_key:
                self.f_tmp = open(res['->>'][0], 'a')
                out_func = self.write_file
            if '-h' in ls_key:
                self.commands[s[0]].show_help(out_func=out_func)
                if self.f_tmp is not None:
                    self.f_tmp.close()
                    self.f_tmp = None
                return None, None, None, None

            return s[0], res, self.commands[s[0]].function, out_func
        except KeyError:
            print("Command not found. Use 'help' command.")
            return None, None, None, print
