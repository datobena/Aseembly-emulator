import re
import operator


M = []
symbols = {
    '+' : operator.add,
    '-' : operator.sub,
    '/' : operator.floordiv,
    '*' : operator.mul,
    'BEQ' : operator.eq,
    'BNE' : operator.ne,
    'BLT' : operator.lt,
    'BLE' : operator.le,
    'BGT' : operator.gt,
    'BGE' : operator.ge
}
types = {
    '.1' : 1,
    '.2' : 2,
    '.8' : 8,
    'd' : 4,
    'u' : -4,
    's' : -1,
    'c' : 1
}
class node:
    def __init__(self, SP = 0):
        self.data = [SP, 0, 0]
        self.var = {
            'SP' : 0,
            'PC' : 1,
            'RV' : 2
        }
        
        
def getBit(y, x):
    return str((x>>y)&1)
def tobin(x, count=8):
    shift = range(count-1, -1, -1)
    bits = map(lambda y: getBit(y, x), shift)
    return "".join(bits)
def tomi(i):
    return (-1)*i - 1

def flip(val, tip):
    return 2 ** (tip*8) - val
def toType(val, tip):
    res = tobin(val, tip*8)
    if len(res) <= 8 * tip:
        return val
    res = res[len(res) - 8*tip:len(res)]
    mark = 1
    ans = int(res, 2)
    if res[0] == '1':
        ans = flip(ans, tip)
        mark = -1
    return mark*ans
def getM(idx, tip):
    isUnsigned = (tip < 0)
    idx = tomi(idx)
    res = ''
    mark = 1
    if isUnsigned:
        tip = tip*(-1)
    for i in range(0, tip):
        res = M[idx - i] + res
    ans = int(res, 2)
    if not isUnsigned and res[0] == '1':
        ans = flip(ans, tip)
        mark = -1
    return mark*ans
def doright(box, start, end, script):
    fun = symbols['+']
    flag = 0
    kind = 4
    ans = 0
    i = start
    while i < end:
        cur = script[i]
        if cur not in symbols:
            if cur in types:
                kind = types[cur]
            elif cur.isnumeric():
                ans = fun(ans, int(cur))
            elif cur == 'M':
                flag+=1
                ret =  doright(box, script.index('[', start, end) + 1, script.index(']', start, end), script)
                flag += ret[2]
                res = getM(ret[0], kind)
                ans = fun(ans, res)
                i = script.index(']', start, end)
            else:
                flag +=1
                ans = fun(ans, box.data[box.var[cur]])
        else:
            fun = symbols[cur]
        i += 1
    return (ans, kind, flag)

def assigntoM(index, tup):
    index = tomi(index)
    val = tobin(tup[0], tup[1]*8)
    byte = tup[1]
    if len(val) < 8 * byte:
        val = '0'*(8*byte - len(val)) + val
    for i in range(0, byte):
        M[index - i] = val[len(val) - 8:len(val)]
        val = val[0 : len(val) - 8]
    
def addzero(size):
    for i in range(0, size):
        M.append('00000000')

def doleft(box, end, script, tup):
    cur = script[0]
    if cur == 'M':
        tu = doright(box, script.index('[') + 1, script.index(']'), script)
        if tup[2] > 1 or tu[2] > 1:
            print('Problem found in code, Line: ' + str(int(box.data[1]/4) + 1) + '!!! ALU, LOAD, STORE is not used properly!')
            exit()
        assigntoM(tu[0], tup)
    else:
        if cur not in box.var:
            box.var[cur] = len(box.var)
            box.data.append(0)
        i = box.var[cur]
        if tup[2] > 2:
            print('Problem found in code, Line: ' + str(int(box.data[1]/4) + 1) + '!!! ALU, LOAD, STORE is not used properly!')
            exit()
        box.data[i] = toType(tup[0], tup[1])
def docompare(box, script):
    arr = []
    first = 0
    second = 0
    fun = symbols[script[0]]
    if script[1].isnumeric():
        first = int(script[1])
    else:
        first = box.data[box.var[script[1]]]
    if script[2].isnumeric():
        second = int(script[2])
    else:
        second = box.data[box.var[script[2]]]
    if fun(first, second):
        box.data[1] = doright(box, 3, len(script), script)[0]
    else:
        box.data[1] += 4
    return

def insert_str(string, mid, index):
    return string[:index] + mid + string[index:]

def getstr(sp):
    i = 0
    toprint = ""
    while sp + i != 0:
        c = chr(getM(sp + i, 1))
        if c == '\0':
            break
        toprint += c
        i += 1
    return toprint

# When calling print in assembly, doprint function is provoked, in stack, 
# bytes on top of it are representing null terminated string, and after that we have variables,
# which are replacements for %d type variables, as we have in C and C++ printf. 
def doprint(box):
    sp = box.data[box.var['SP']]
    toprint = ''
    variables = []
    i = 0
    varsfound = 0
    while sp + i != 0:
        c = chr(getM(sp + i, 1))
        if c == '\0':
            break
        if c == '%':
            tip = types[chr(getM(sp + i + 1, 1))]
            variables.append((tip, i - varsfound*2))
            i += 1
            varsfound += 1
        else:
            toprint += c
        i += 1
    sp = sp + i + 1
    added = 0
    for tup in variables:
        if tup[0] == -1:
            cur = getstr(sp)
            sp += len(cur) + 1
            toprint = insert_str(toprint, cur, tup[1] + added)
        else:
            cur = getM(sp, tup[0])
            if tup[0] == 1:
                cur = chr(cur)
            else:
                cur = str(cur)
            sp += tup[0]
            toprint = insert_str(toprint, cur, tup[1] + added)
        added += len(cur)
    print(toprint)


def strlen(box):
    i = 0
    sp = box.data[box.var['SP']]
    while sp + i != 0:
        c = getM(sp + i, 1)
        if c == 0:
            return i
        i += 1
    return -1

pre_defined_funcs = {
    'printf' : doprint,
    'strlen' : strlen
}

def start(box, name, lines, functions):
    box.data[1] = functions[name] * 4
    while int(box.data[1]/4) < len(lines) and not lines[int(box.data[1]/4)].startswith('RET'):
        nusize = box.data[0] * (-1)
        if nusize > len(M):
            addzero(nusize - len(M))
        cur = lines[int(box.data[1]/4)]
        script = list(filter(None, re.split('([=\[\]+\-*/])|[, <>]', cur)))
        for i in range(0, len(script)):
            script[i] = script[i].strip()
        script = list(filter(None, script))
        if not script[0] == 'CALL':
            if script[0] == 'JUMP':
                box.data[1] = doright(box, 1, len(script), script)[0]
                continue
            elif script[0].startswith('B'):
                docompare(box, script)
                continue
            else:
                eqi = script.index('=')
                doleft(box, eqi, script, doright(box, eqi + 1, len(script), script))
        else:
            funcname = script[1]
            if funcname in functions:
                box.data[0] -= 4
                newnode = node(box.data[0])
                box.data[box.var['RV']] = start(newnode, funcname, lines, functions)
                box.data[0] += 4
            elif funcname in pre_defined_funcs:
                fun = pre_defined_funcs[funcname]
                RV = fun(box)
                if RV is not None:
                    box.data[box.var['RV']] = RV
        box.data[1] += 4
    return box.data[box.var['RV']]
def main():
    folder = "Enter path where tests are located here"
    filename = input("Please input the file name or press Enter: ")
    if filename == '':
        filename = 'hello_world'
    afile = open(folder + filename, "r")
    lines = afile.readlines()
    tokens = []
    functions = {}
    for line in lines:
        token = re.split('[\n\t;]', line)
        tokens += list(filter(None, token))
    lines = []
    counter = 0
    for token in tokens:
        if token[len(token) - 1] == ':':
            functions[token.split(':')[0]] = counter + 1
        counter+=1
    assert('main' in functions)
    first = node()
    print("Return value: " + str(start(first, 'main', tokens, functions)))

# Start the program
main()