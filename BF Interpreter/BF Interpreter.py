# -*- coding: UTF-8 -*-
# python 3.6 using PyCharm
# BrainF*ck Interpreter
# vbcpascal

# July 11th


class BrainF(object):
    def __init__(self, code="", size=1000, num_input=[], opt=1):
        self.size = size
        self.code = code
        self.array = [0] * size
        self.input = num_input
        self.ptr = 0
        self.code_ptr = 0
        self.loop_str = {}
        self.cmd = {'+': self.inc_val,    '-': self.dec_val,
                    '>': self.inc_ptr,    '<': self.dec_ptr,
                    '.': self.prt,        ',': self.rd,
                    '[': self.loop_begin, ']': self.loop_end}
        self.get_loop_pos(code)
        self.ptr = 0
        self.opt = opt
        self.driver_loop()

    def get_loop_pos(self, code):
        loop_begin = []
        for p in range(len(code)):
            if code[p] is '[':
                loop_begin.append(p)
            elif code[p] is ']':
                self.loop_str[p] = loop_begin[len(loop_begin) - 1]
                self.loop_str[loop_begin.pop()] = p

    def inc_val(self):      # +
        self.array[self.ptr] += 1
        return 0

    def dec_val(self):      # -
        self.array[self.ptr] -= 1
        return 0

    def inc_ptr(self):      # >
        if self.ptr == self.size - 1:
            self.ptr = 0
        else:
            self.ptr += 1
        return 0

    def dec_ptr(self):      # <
        if self.ptr == 0:
            self.ptr = self.size - 1
        else:
            self.ptr -= 1
        return 0

    def prt(self):          # .
        if (get_bit(self.opt, 5)):
            print(self.array[self.ptr], end="")
        else:
            try:
                print(chr(self.array[self.ptr]), end="")
            except:
                print('[Ascii not in range]', end="")
        return 0

    def rd(self):           # ,
        self.array[self.ptr] = self.input[0]
        self.input = self.input[1:]
        return 0

    def loop_begin(self):   # [
        if self.array[self.ptr] is 0:
            self.code_ptr = self.loop_str[self.code_ptr]
        return 0

    def loop_end(self):     # ]
        if self.array[self.ptr] is not 0:
            self.code_ptr = self.loop_str[self.code_ptr]
        return 0

    def driver_loop(self):
        while self.code_ptr is not len(self.code):
            c = self.code[self.code_ptr]
            if c in '+-<>,.[]':
                self.cmd[c]()
            self.code_ptr += 1
        return 0


def get_input_num(str="", cnt=0, IgnoreError=0):
    lst = str.split()
    for i in range(len(lst)):
        try:
            lst[i] = int(lst[i])
        except ValueError:
            if IgnoreError: lst[i] = 0
            else: return 2
    if (not IgnoreError) and (len(lst) != cnt):
        return 3
    if len(lst) < cnt:
        lst += [0]*(cnt - len(lst))
    elif len(lst) > cnt:
        lst = lst[0:cnt - 1]
    return lst


def input_options(args):
    # return: [0.exit? 1.-e 2.-o 3.-s 4.-f 5.-p]
    c = args[0]
    args = args[1:]
    res = 0
    if c == 'E': return -100
    elif c == 'R':
        res = 1
        if '-E' in args: res += (1 << 1)
        if '-O' in args: res += (1 << 2)
        if '-S' in args: res += (1 << 3)
        if '-F' in args: res += (1 << 4)
        if '-P' in args: res += (1 << 5)
        return res
    elif c == 'H':
        print('BrainF*ck Interpreter, version 0.1.0')
        if '-C' not in args:
            print('E\n描述：退出程序\n')
            print('H [-B] [-C]\n描述：获取帮助\n参数列表：')
            print('  -B    显示Brainf*ck帮助信息')
            print('  -C    关闭本程序的帮助信息')
            print()
            print('R [-E] [-O] [-S] [-F] [-P]\n描述：运行代码\n参数列表：')
            print('  -E   打开拓展功能（暂时不存在的）')
            print('  -O   输入仅一行')
            print('  -S   使用默认的size = 1000')
            print('  -F   用0填充数据的非法输入')
            print('  -P   输出位置本身对应数字代替对应Ascii值')
        if '-B' in args:
            print('\nBrainf*ck语言简要帮助：')
            print('  >    指针加一')
            print('  <    指针减一')
            print('  +    指针指向的字节的值加一')
            print('  -    指针指向的字节的值减一')
            print('  .    输出指针指向的单元内容（ASCⅡ码）')
            print('  ,    输入内容到指针指向的单元（ASCⅡ码）')
            print('  [    如果指针指向的单元值为零，向后跳转到对应的]指令的次一指令处')
            print('  ]    如果指针指向的单元值不为零，向前跳转到对应的[指令的次一指令处')
    return 0


def get_bit(x, pos):
    return (x >> pos) & 1


def work():
    print()
    print('What do you want to do?')
    print('R. Run the code')
    print('H. Help')
    print('E. Exit(0)')
    c = input('>>> ')
    c = input_options(c.upper().split())
    if c == -100:   # exit
        return -100
    elif c == 0:    # 'H' or Input Error
        return 0
    else:
        if get_bit(c, 3): size = 1000
        else:
            size = input('Input size of the array: ')
            try:
                size = int(size)
            except ValueError:
                return 1  # 1: unexpected input value type

        code = ""

        if get_bit(c, 2):
            code = input('Input the code: \n$ ')
        else:
            print('Input the code: (use "/end" to end edit)')
            while True:
                tmp_code = input('$ ')
                if tmp_code == '/end': break
                code += tmp_code

        cnt = code.count(',')
        if cnt is 0:
            res = []
        else:
            num_input = input('Input the number (Total %d): ' % (cnt))
            res = get_input_num(num_input, cnt, get_bit(c, 4))
            if res == 2: return 2  # 2: Wrong value type in Input
            if res == 3: return 3  # 3: Wrong number of Input
        BrainF(code, size, res, c)
        print('Process finished with exit code 0')
        return 0


def main():
    print('Welcome to use Brainf*ck interpreter 0.1.0')
    while True:
        e = work()
        if e == 0: continue
        elif e == -100: break
        # print()
        if e == -1: print('Error(%d): Input Error' % e)
        elif e == 1: print('Error(%d): Unexpected input value type' % e)
        elif e == 2: print('Error(%d): Wrong value type in Input' % e)
        elif e == 3: print('Error(%d): Wrong number of Input' % e)
    return 0


main()

# BrainF(" ++++++ [ > ++++++++++ < - ] > +++++ .")
# BrainF(",>,< [ > [ >+ >+ << -] >> [- << + >>] <<< -] >> .", 10, [3, 4])
