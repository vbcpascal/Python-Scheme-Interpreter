import sys
import math
import operator as op
import numpy as np

# 特殊类型声明
Symbol = str
List = list
Number = (int, float)


# 特殊函数/基本过程
def car(lst): return lst[0]
def cdr(lst): return lst[1:]
def cons(x, y):
    if isinstance(y, list):
        return [x] + y
    else:
        return [x, y]

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
    
# 过程/环境类
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

# 解释器类（接收 ['+', 1, 2] 列表）
class Interpreter(object):
    def __init__(self):
        self.env = self.setup_env()
        self.code = ''
        self.output = ''
        
    def getResult(self, code):
        self.code = code
        try:
            self.output = self.eval(self.code, self.env)
        except Exception as e:
            self.output = ('%s: %s' %(type(e).__name__, e))
        return self.output
        

    def tagged_list(self, exp, str):
        if str == 'self_evaluating':
            return isinstance(exp, Number) #or isinstance(exp, **String**)
        elif str == 'variable':
            return isinstance(exp, Symbol)
        elif str == 'application':
            return isinstance(exp, Procedure)
        elif str == 'assignment':
            return exp[0] == 'set!'
        elif str == 'definition':
            return exp[0] == 'define'
        else:
            return exp[0] == str

    def eval(self, exp, env):
        if exp == []:
            return
        elif self.tagged_list(exp, 'self_evaluating'):
            # if debugRunProcess: print(exp)
            return exp
        elif self.tagged_list(exp, 'variable'):
            return env.lookup(exp)[exp]
        elif self.tagged_list(exp, 'quoted'):
            (_, text) = exp
            return text
        elif self.tagged_list(exp, 'assignment'):
            (_, variable, value) = exp
            env.lookup(variable)[variable] = self.eval(value, env)
            return
        elif self.tagged_list(exp, 'definition'):
            variable = exp[1]
            if isinstance(variable, list):
                variable, value = car(variable), ["lambda", cdr(variable)] + exp[2:]
            else:
                value = exp[2]
            env[variable] = self.eval(value, env)
            return
        elif self.tagged_list(exp, 'if'):
            (_, predicate, consequent, alternative) = exp
            res = (self.eval(consequent, env) if self.eval(predicate, env) else self.eval(alternative, env))
            return res
        elif self.tagged_list(exp, 'and'):
            exps = cdr(exp)
            return self.eval_and(exps, env)
        elif self.tagged_list(exp, 'lambda'):
            parameters = exp[1]
            body = exp[2:]
            return Procedure(parameters, body, env)
        elif self.tagged_list(exp, 'begin'):
            actions = cdr(exp)
            return self.eval_seq(actions, env)
        else:   # tagged_list(exp, 'application'):
            print('proc:' + str(exp))
            return self.my_apply(self.eval(exp[0], env), self.value_list(exp[1:], env))

    def my_apply(self, proc, arguments):
        if isinstance(proc, Procedure):
            return self.eval_seq(proc.body, Env(proc.parameters, arguments, proc.env))
        else:
            return proc(*arguments)

    def value_list(self, exps, env):
        res = []
        for exp in exps:
            res.append(self.eval(exp, env))
        return res

    def eval_seq(self, exps, env):
        if cdr(exps) == []:
            return self.eval(car(exps), env)
        else:
            self.eval(car(exps), env)
            return self.eval_seq(cdr(exps), env)

    def eval_and(self, exps, env):
        if exps is []:
            return True
        elif cdr(exps) is []:
            return self.eval(car(exps), env)
        elif self.eval(car(exps), env) is False:
            return False
        else:
            return self.eval_and(cdr(exps), env)

    def eval_or(self, exps, env):
        if exps is []:
            return True
        elif cdr(exps) is []:
            return self.eval(car(exps), env)
        elif self.eval(car(exps), env) is True:
            return True
        else:
            return self.eval_or(cdr(exps), env)

    def setup_env(self):
        env = Env()
        env.update(vars(math))
        env.update(primitive_procedures)
        return env