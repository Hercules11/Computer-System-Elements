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

preString = {}


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
    completePath = '\\'.join(path.split('\\')[:-1]) + '\\' + newFileName.split('.')[0] + ".xml"
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
                    toFile.write(classification(token) + '\n')
                    token = ""
                continue
            if isTogether(token, char):
                token += char
            else:
                toFile.write(classification(token) + '\n')
                token = char
        break
    toFile.write("</tokens>")
    fileHandler.close()
    toFile.close()


filePath = sys.argv[1]
if os.path.isfile(filePath):
    fileTokenizer(filePath)
    # fileParser(filePath)
else:
    for file in os.listdir(filePath):
        if file.endswith(".jack"):
            fileTokenizer(filePath + '\\' + file)
            # fileParser(filePath + '\\' + file)
