import os
import sys

keyword = ['class', 'constructor', 'function',
           'method', 'field', 'static', 'var', 'int',
           'char', 'boolean', 'void', 'true', 'false',
           'null', 'this', 'let', 'do', 'if', 'else',
           'while', 'return']

symbol = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
          '/', '&', '|', '<', '>', '=', '~']

number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# 预处理文件中的字符串
preString = {}

# 把tokenize过程中的token拿出来
cleanToken = []

# 存储parse过程中的block parent node
treeStack = []

# 存储parse 后要写入.xml文件的内容
contentList = []


def classification(single):
    if single in keyword:
        return f"<keyword> {single} </keyword>"
    elif single in symbol:
        if single == '<':
            single = "&lt;"
        elif single == '>':
            single = "&gt;"
        elif single == '&':
            single = "&amp;"
        return f"<symbol> {single} </symbol>"
    elif single in preString:
        return f"<stringConstant> {preString[single]} </stringConstant>"
    elif single[0] in number:
        return f"<integerConstant> {single} </integerConstant>"
    else:
        return f"<identifier> {single} </identifier>"


def isTogether(char_one, char_two):
    if len(char_one) == 0:
        return True
    char1 = ord(char_one[-1])
    char2 = ord(char_two)
    if (65 <= char1 <= 90 or 97 <= char1 <= 122 or char1 == 95 or 48 <= char1 <= 57) and \
            (65 <= char2 <= 90 or 97 <= char2 <= 122 or char2 == 95 or 48 <= char2 <= 57):
        return True
    return False


def fileTokenizer(path):
    fileHandler = open(path, 'r')
    newFileName = "to" + path.split('\\')[-1]
    completePath = '\\'.join(path.split('\\')[:-1]) + '\\' + newFileName.split('.')[0] + "T.xml"
    toFile = open(completePath, 'w')

    # strip comments in file
    fileContent = []
    for line in fileHandler:
        line = line.rstrip().lstrip()
        if line.startswith("//") or not line:
            continue
        if "//" in line:
            line = line.split("//")[0].rstrip()
        fileContent.append(line)
    # strip /* */
    fileString = '\n'.join(fileContent) + '\n'
    while True:
        if "/*" in fileString:
            start = fileString.find("/*")
            end = fileString.find("*/")
            fileString = fileString[:start] + fileString[(end + 2):]
        else:
            break

    # precede to handle string object
    while True:
        if "\"" in fileString:
            start = fileString.find("\"")
            a = fileString.find("\";")
            b = fileString.find("\")")
            if "\";" in fileString and "\")" in fileString:
                end = a if a < b else b
            else:
                end = a if a > b else b
            preString[str(abs(hash(fileString[(start + 1):end])))] = fileString[(start + 1):end]
            fileString = fileString.replace(fileString[start:(end + 1)], str(abs(hash(fileString[(start + 1):end]))))
        else:
            break

    toFile.write("<tokens>\n")
    while True:
        token = ""
        for char in fileString:
            if char == '\n' or char == ' ':
                if len(token) != 0:
                    cleanToken.append(token)
                    toFile.write(classification(token) + '\n')
                    token = ""
                continue
            if isTogether(token, char):
                token += char
            else:
                cleanToken.append(token)
                toFile.write(classification(token) + '\n')
                token = char
        break
    toFile.write("</tokens>")
    fileHandler.close()
    toFile.close()


#########################################################################################################
# analyzer part ↑ ↑ ↑
# -------------------------------------------------------------------------------------------------------
# parser part ↓ ↓ ↓ ↓
# 根据原书208页 Jack语法构建函数
#########################################################################################################
def classCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<class>")
    treeStack.append("class")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # class
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # className
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # {
    while tokens[0] in ['static', 'field']:
        classVarDecCompile(tokens)
    while tokens[0] in ['constructor', 'function', 'method']:
        subroutineDecCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # }
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</class>")


def classVarDecCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<classVarDec>")
    treeStack.append("classVarDec")
    while tokens[0] != ';':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ;
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</classVarDec>")


def subroutineDecCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<subroutineDec>")
    treeStack.append("subroutineDec")
    while tokens[0] != '(':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # （
    parameterListCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # )
    subroutineBodyCompile(tokens)
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</subroutineDec>")


def parameterListCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<parameterList>")
    treeStack.append("parameterList")
    while tokens[0] != ')':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</parameterList>")


def subroutineBodyCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<subroutineBody>")
    treeStack.append("subroutineBody")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # {
    while tokens[0] == 'var':
        varDecCompile(tokens)
    while tokens[0] in ['let', 'if', 'while', 'do', 'return']:
        statementsCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # }
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</subroutineBody>")


def varDecCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<varDec>")
    treeStack.append("varDec")
    while tokens[0] != ';':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ;
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</varDec>")


def statementsCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<statements>")
    treeStack.append("statements")
    while tokens[0] in ['let', 'if', 'while', 'do', 'return']:
        if tokens[0] == 'let':
            letStatementCompile(tokens)
        elif tokens[0] == 'if':
            ifStatementCompile(tokens)
        elif tokens[0] == 'while':
            whileStatementCompile(tokens)
        elif tokens[0] == 'do':
            doStatementCompile(tokens)
        elif tokens[0] == 'return':
            returnStatementCompile(tokens)
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</statements>")


def letStatementCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<letStatement>")
    treeStack.append("letStatement")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # let
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # varName
    if tokens[0] == '[':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # [
        expressionCompile(tokens)
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ]
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # =
    expressionCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ;
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</letStatement>")


def ifStatementCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<ifStatement>")
    treeStack.append("ifStatement")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # if
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # (
    expressionCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # )
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # {
    statementsCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # }
    if tokens[0] == 'else':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # else
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # {
        statementsCompile(tokens)
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # }
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</ifStatement>")


def whileStatementCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<whileStatement>")
    treeStack.append("whileStatement")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # while
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # (
    expressionCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # )
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # {
    statementsCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # }
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</whileStatement>")


def doStatementCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<doStatement>")
    treeStack.append("doStatement")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # do
    subroutineCallCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ;
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</doStatement>")


def returnStatementCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<returnStatement>")
    treeStack.append("returnStatement")
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # return
    if tokens[0] != ';':
        expressionCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ;
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</returnStatement>")


def expressionCompile(tokens):
    opList = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    contentList.append('  ' * len(treeStack) + "<expression>")
    treeStack.append("expression")
    termCompile(tokens)
    while tokens[0] in opList:
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # op
        termCompile(tokens)
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</expression>")


# 这里非常怕发生干涉
def termCompile(tokens):
    # KeywordConstant = ['true', 'false', 'null', 'this']
    unaryOp = ['-', '~']
    contentList.append('  ' * len(treeStack) + "<term>")
    treeStack.append("term")
    if tokens[0] in unaryOp:
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # unaryOp
        termCompile(tokens)
    elif tokens[0] == '(':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # (
        expressionCompile(tokens)
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # )
    elif tokens[1] == '[':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # varName
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # [
        expressionCompile(tokens)
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ]
    elif tokens[1] in ['(', '.']:
        subroutineCallCompile(tokens)
    else:
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # varName|Constant
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</term>")


def subroutineCallCompile(tokens):
    if tokens[1] == '.':
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # className|varName
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # .
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # subroutineName
    else:
        contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # subroutineName
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # (
    expressionListCompile(tokens)
    contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # )


def expressionListCompile(tokens):
    contentList.append('  ' * len(treeStack) + "<expressionList>")
    treeStack.append("expressionList")
    if tokens[0] != ')':
        expressionCompile(tokens)
        while tokens[0] == ',':
            contentList.append('  ' * len(treeStack) + classification(tokens.pop(0)))  # ,
            expressionCompile(tokens)
    treeStack.pop(-1)
    contentList.append('  ' * len(treeStack) + "</expressionList>")


def fileParser(path):
    newFileName = "to" + path.split('\\')[-1]
    completePath = '\\'.join(path.split('\\')[:-1]) + '\\' + newFileName.split('.')[0] + ".xml"
    toFile = open(completePath, 'w')
    print(cleanToken)
    # classCompile(cleanToken)
    for line in contentList:
        toFile.write(line + '\n')
    toFile.close()


filePath = sys.argv[1]
if os.path.isfile(filePath):
    fileTokenizer(filePath)
    fileParser(filePath)
    contentList = []  # 置为空
else:
    for file in os.listdir(filePath):
        if file.endswith(".jack"):
            fileTokenizer(filePath + '\\' + file)
            fileParser(filePath + '\\' + file)
            contentList = []  # 置为空
