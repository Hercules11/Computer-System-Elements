# 存储编译好的 vm 代码
content = []


# 处理程序中的 classVar, 编译整个文件时调用
def classSymbolTable(tokens):
    token = tokens[:]  # don't change source list
    symbolDict = {
        "name": [],
        "type": [],
        "kind": [],
        "index": []
    }
    while len(token) > 0:
        if token[0] in ['field', 'static']:
            newItemKind = token.pop(0)
            newItemType = token.pop(0)
            while True:
                symbolDict["name"].append(token.pop(0))
                symbolDict["type"].append(newItemType)
                symbolDict["kind"].append(newItemKind)
                symbolDict["index"].append(symbolDict["kind"].count(newItemKind) - 1)
                if token.pop(0) == ',':
                    continue
                else:
                    break
        else:
            token.pop(0)
    # print(symbolDict)


# 处理函数中的 subroutineDec, 处理函数时调用
# 参考原书208页 Jack 语法
def subroutineSymbolTable(tokens, className=None):
    token = tokens[:]  # don't change source list
    symbolDict = {
        "name": [],
        "type": [],
        "kind": [],
        "index": []
    }
    subroutineType = token[0]
    if subroutineType == 'method':
        symbolDict["name"].append("this")
        symbolDict["type"].append(className)
        symbolDict["kind"].append("argument")
        symbolDict["index"].append(0)
    parameterList = token[(token.index('(')):(token.index(')'))]
    while len(parameterList) > 1:
        parameterList.pop(0)  # de-( | de-,
        symbolDict["type"].append(parameterList.pop(0))  # type
        symbolDict["name"].append(parameterList.pop(0))  # varName
        symbolDict["kind"].append("argument")
        symbolDict["index"].append(symbolDict["kind"].count("argument") - 1)
    while len(token):
        if token[0] in ['var']:
            token.pop(0)  # de-var
            newItemType = token.pop(0)
            while True:
                symbolDict["name"].append(token.pop(0))
                symbolDict["type"].append(newItemType)
                symbolDict["kind"].append("local")
                symbolDict["index"].append(symbolDict["kind"].count("local") - 1)
                if token.pop(0) == ',':
                    continue
                else:
                    break
        else:
            token.pop(0)
    # print(symbolDict)


def expCodeWriter(tokens):
    pass


def vmWriter(tokens):
    pass
