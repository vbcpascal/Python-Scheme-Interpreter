# python 3.6 using PyCharm
# Scheme Interpreter
# vbcpascal

# July 11th

import math
import operator as op

Symbol = str
List = list
Number = (int, float)

class Procedure(object):
    def __init__(self, parameters, body, env):
        self.parameters, self.body, self.env = parameters, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.parameters, args, self.env))

class Env(dict):
    def __init__(self, names=(), objects=(), enclosing=None):
        self.update(zip(names, objects))
        self.enclosing = enclosing

    def lookup(self, var):
        return self if (var in self) else self.enclosing.lookup(var)

def car(lst): return lst[0]
def cdr(lst): return lst[1:]
def cons(x, y):
    if isinstance(y, list):
        return [x] + y
    else:
        return [x, y]

def tagged_list(exp, str):
    if str == 'self_evaluating':
        return isinstance(exp, Number) #or isinstance(exp, **String**)
    elif str == 'variable':
        return isinstance(exp, Symbol)
    elif str == 'application':
        return isinstance(exp, Procedure)
    elif str == "quoted":
        return exp[0] == 'quote'
    elif str == 'assignment':
        return exp[0] == 'set!'
    elif str == 'definition':
        return exp[0] == 'define'
    else:
        return exp[0] == str

def eval(exp, env):
    if exp == []:
        return
    elif tagged_list(exp, 'self_evaluating'):
        return exp
    elif tagged_list(exp, 'variable'):
        return env.lookup(exp)[exp]
    elif tagged_list(exp, 'quoted'):
        (_, text) = exp
        return text
    elif tagged_list(exp, 'assignment'):
        (_, variable, value) = exp
        env.lookup(variable)[variable] = eval(value, env)
        return
    elif tagged_list(exp, 'definition'):
        variable = exp[1]
        if isinstance(variable, list):
            variable, value = car(variable), ["lambda", cdr(variable)] + exp[2:]
        else:
            value = exp[2]
        env[variable] = eval(value, env)
        return
    elif tagged_list(exp, 'if'):
        (_, predicate, consequent, alternative) = exp
        res = (consequent if eval(predicate, env) else alternative)
        return res
    elif tagged_list(exp, 'and'):
        exps = cdr(exp)
        return eval_and(exps, env)
    elif tagged_list(exp, 'lambda'):
        parameters = exp[1]
        body = exp[2:]
        return Procedure(parameters, body, env)
    elif tagged_list(exp, 'begin'):
        actions = cdr(exp)
        return eval_seq(actions, env)
    else:   # tagged_list(exp, 'application'):
        return my_apply(eval(exp[0], env), value_list(exp[1:], env))

def my_apply(proc, arguments):
    if isinstance(proc, Procedure):
        return eval_seq(proc.body, Env(proc.parameters, arguments, proc.env))
    else:
        return proc(*arguments)

def value_list(exps, env):
    res = []
    for exp in exps:
        res.append(eval(exp, env))
    return res

def eval_seq(exps, env):
    if cdr(exps) == []:
        return eval(car(exps), env)
    else:
        eval(car(exps), env)
        return eval_seq(cdr(exps), env)

def eval_and(exps, env):
    if exps is []:
        return True
    elif cdr(exps) is []:
        return eval(car(exps), env)
    elif eval(car(exps), env) is False:
        return False
    else:
        return eval_and(cdr(exps), env)

def eval_or(exps, env):
    if exps is []:
        return True
    elif cdr(exps) is []:
        return eval(car(exps), env)
    elif eval(car(exps), env) is True:
        return True
    else:
        return eval_or(cdr(exps), env)

primitive_procedures = {
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.floordiv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        'car': car,
        'cdr': cdr,
        'cons': cons,
        'append': op.add,
        'length': len,
        'not': op.not_,
        'eq?': op.is_,
        'equal?': op.eq,
        'caar': lambda x: car(car(x)),
        'cadr': lambda x: car(cdr(x)),
        'cdar': lambda x: cdr(car(x)),
        'cddr': lambda x: cdr(cdr(x)),
        'list': lambda *x: list(x),
        'null?': lambda x: x == [],
        'pair?': lambda x: isinstance(x, list),
        'list?': lambda x: isinstance(x, list),
        'true?': lambda x: x == True,
        'false?': lambda x: x != True,
        'number?': lambda x: isinstance(x, Number),
        'symbol?': lambda x: isinstance(x, Symbol),
        'newline': lambda: print(),
        'display': lambda x: print(x, end=""),
        'displayln': lambda x: print(x),
    }

def setup_env():
    env = Env()
    env.update(vars(math))
    env.update(primitive_procedures)
    return env

def pretrans(code):
    code = code.replace('(', ' ( ').replace(')', ' ) ')
    code = code.replace('[', ' [ ').replace(']', ' ] ')
    code = code.replace('"', ' " ').replace(';', ' ; ')
    code = code.replace('#|', ' #| ').replace('|#', ' |# ')
    code = code.split()
    return code

def parse(exps):
    code = exps.pop(0)
    if code == '(':
        res=[]
        while exps[0] != ')':
            res.append(parse(exps))
        exps.pop(0)
        return res
    if code == '[':
        res=[]
        while exps[0] != ']':
            res.append(parse(exps))
        exps.pop(0)
        return res
    elif code == '"':
        res = []
        while exps[0] != '"':
            res.append(parse(exps))
        exps.pop(0)
        res_str = '"'
        res_str += " ".join(res)
        res_str += '"'
        return ['quote', res_str]
    else:
        return atom(code)

def atom(code):
    try:
        return int(code)
    except ValueError:
        try:
            return float(code)
        except ValueError:
            return Symbol(code)

def to_Scheme_code(exps):
    return exps

def driver_loop():
    env = setup_env()
    while True:
        str = input()
        if input == "":
            continue
        try:
            if str == "/end":
                break
            output = eval(parse(pretrans(str)), env)
            if output is not None:
                print(to_Scheme_code(output))
        except Exception as e:
            print('%s: %s' %(type(e).__name__, e))

driver_loop()
