className = ""
classSymbolTable = {
    "name": [],
    "type": [],
    "kind": [],
    "index": []
}
subroutineSymbolTable = {
    "name": [],
    "type": [],
    "kind": [],
    "index": []
}
resultContent = []


# 处理程序中的 classVar
def classSymbol(tokens):
    itemKind = tokens.pop(0)  # static | field
    itemType = tokens.pop(0)  # type
    while True:
        itemName = tokens.pop(0)  # varName
        classSymbolTable["name"].append(itemName)
        classSymbolTable["type"].append(itemType)
        classSymbolTable["kind"].append(itemKind)
        hadNumber = classSymbolTable["index"].count(itemKind)
        classSymbolTable["index"].append(hadNumber)
        if tokens.pop(0) == ';':
            break


# 处理函数中的 parameterList and varDec
def subroutineSymbol(tokens):
    subroutineKind = tokens.pop(0)  # constructor | function | method
    if subroutineKind == "method":
        classSymbolTable["name"].append("this")
        classSymbolTable["type"].append(className)
        classSymbolTable["kind"].append("argument")
        classSymbolTable["index"].append(0)
    subroutineType = tokens.pop(0)  # void | type
    subroutineName = tokens.pop(0)
    tokens.pop(0)  # de-(
    while tokens[0] != ')':
        parameterType = tokens.pop(0)
        parameterName = tokens.pop(0)
        classSymbolTable["name"].append(parameterName)
        classSymbolTable["type"].append(parameterType)
        classSymbolTable["kind"].append("argument")
        hadNumber = classSymbolTable["kind"].count("argument")
        classSymbolTable["index"].append(hadNumber)
        if tokens.pop(0) == ',':
            continue
        else:
            break
    tokens.pop(0)  # de-{
    while tokens[0] == 'var':
        varKind = tokens.pop(0)  # var
        varType = tokens.pop(0)  # type
        while True:
            varName = tokens.pop(0)
            subroutineSymbolTable["name"].append(varName)
            subroutineSymbolTable["type"].append(varType)
            subroutineSymbolTable["kind"].append(varKind)
            hadNumber = subroutineSymbolTable["kind"].count("var")
            subroutineSymbolTable["index"].append(hadNumber)
            if tokens.pop(0) == ';':
                break
    resultContent.append(f"function {className+'.'+subroutineName} {subroutineSymbolTable['kind'].count('argument')}")
    # 建立 subroutineSymbolTable 后进行写 vm 命令
    statementsWriter(tokens)
    tokens.pop(0)  # de-end }


#######################################################################################################
# 构建符号表 Part I  ↑ ↑ ↑
# -----------------------------------------------------------------------------------------------------
# vmWriter Part II  ↓ ↓ ↓
# 根据原书 208 页, Jack 语法以及 233 页的映射规范构建函数
#######################################################################################################
def expressionListWriter(tokens):
    pass


def subroutineCallWriter(tokens):
    pass


def termWriter(tokens):
    unaryOp = {'-': "eq", '~': "not"}
    if tokens[0] in unaryOp:
        unary_op = tokens.pop(0)
        termWriter(tokens)
        resultContent.append(f"{unaryOp[unary_op]}")
    elif tokens[0] == '(':
        tokens.pop(0)  # (
        expressionWriter(tokens)
        tokens.pop(0)  # )
    elif tokens[1] == '[':
        if tokens[0] in subroutineSymbolTable["name"]:
            varLocation = subroutineSymbolTable["name"].index(tokens[0])
            varKind = subroutineSymbolTable['kind'][varLocation]
            varIndex = subroutineSymbolTable['index'][varLocation]
        else:
            varLocation = classSymbolTable["name"].index(tokens[0])
            varKind = classSymbolTable['kind'][varLocation]
            varIndex = classSymbolTable['index'][varLocation]
        tokens.pop(0)  # varName
        resultContent.append(f"push {varKind} {varIndex}")
        tokens.pop(0)  # [
        expressionWriter(tokens)
        tokens.pop(0)  # ]
        resultContent.append("add")
        resultContent.append("pop pointer 1")
        expressionWriter(tokens)
        resultContent.append("pop that 0")
    elif tokens[1] in ['(', '.']:
        subroutineCallWriter(tokens)
    else:
        pass


def expressionWriter(tokens):
    opList = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    opDict = {
        '+': "add",
        '-': "sub",
        '*': "call Math.multiply 2",
        '/': "call Math.divide 2",
        '=': "eq",
        '<': "lt",
        '>': "gt",
        '&': "and",
        '|': "or",
    }
    termWriter(tokens)
    if tokens[0] in opList:
        op = tokens.pop(0)
        expressionWriter(tokens)
        resultContent.append(f"{opDict[op]}")


def returnWriter(tokens):
    tokens.pop(0)  # return
    if tokens[0] != ';':
        expressionWriter(tokens)
    else:
        resultContent.append(f"push constant 0\nreturn")
    tokens.pop(0)  # ;


def doWriter(tokens):
    tokens.pop(0)  # do
    subroutineCall(tokens)
    tokens.pop(0)


def whileWriter(tokens):
    tokens.pop(0)  # while
    tokens.pop(0)  # (
    expressionWriter(tokens)
    tokens.pop(0)  # )
    tokens.pop(0)  # {
    statementsWriter(tokens)
    tokens.pop(0)  # }


def ifWriter(tokens):
    tokens.pop(0)  # if
    tokens.pop(0)  # (
    expressionWriter(tokens)
    tokens.pop(0)  # )
    tokens.pop(0)  # {
    statementsWriter(tokens)
    tokens.pop(0)  # }
    if tokens[0] == 'else':
        tokens.pop(0)  # else
        tokens.pop(0)  # {
        statementsWriter(tokens)
        tokens.pop(0)  # }


def letWriter(tokens):
    tokens.pop(0)  # let
    if tokens[0] in subroutineSymbolTable["name"]:
        varLocation = subroutineSymbolTable["name"].index(tokens[0])
        varKind = subroutineSymbolTable['kind'][varLocation]
        varIndex = subroutineSymbolTable['index'][varLocation]
        assignVal = f"pop {varKind} {varIndex}"
    else:
        varLocation = classSymbolTable["name"].index(tokens[0])
        varKind = classSymbolTable['kind'][varLocation]
        varIndex = classSymbolTable['index'][varLocation]
        assignVal = f"pop {varKind} {varIndex}"
    tokens.pop(0)  # varName
    if tokens[1] == '[':
        resultContent.append(f"push {varKind} {varIndex}")
        tokens.pop(0)  # [
        expressionWriter(tokens)
        tokens.pop(0)  # ]
        resultContent.append("add")
        resultContent.append("pop pointer 1")
        expressionWriter(tokens)
        resultContent.append("pop that 0")
    else:
        tokens.pop(0)  # =
        expressionWriter(tokens)
        resultContent.append(assignVal)
        tokens.pop(0)  # ;


def statementsWriter(tokens):
    while tokens[0] in ['let', 'if', 'while', 'do', 'return']:
        if tokens[0] == 'let':
            letWriter(tokens)
        elif tokens[0] == 'if':
            ifWriter(tokens)
        elif tokens[0] == 'while':
            whileWriter(tokens)
        elif tokens[0] == 'do':
            doWriter(tokens)
        elif tokens[0] == 'return':
            returnWriter(tokens)


def vmWriter(tokens):
    tokens.pop(0)  # class
    global className, classSymbolTable, subroutineSymbolTable
    className = tokens.pop(0)  # class_name
    tokens.pop(0)  # de-{
    while tokens[0] in ['static', 'field']:
        classSymbol(tokens)
    while tokens[0] in ['constructor', 'function', 'method']:
        subroutineSymbol(tokens)
        subroutineSymbolTable = {
            "name": [],
            "type": [],
            "kind": [],
            "index": []
        }  # 每一个 subroutine 处理完后, subroutine 符号表置空
    tokens.pop(0)  # de-end }
