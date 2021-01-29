import sys

# read path/file, relative path. eg. add/Add.asm
fileName = sys.argv[1]
fileHandle = open(fileName, 'r')
fileLines = []

JUMP = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

DEST = {
    "null": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

SYMBOL = {
    "SP": "0",
    "LCL": "1",
    "ARG": "2",
    "THIS": "3",
    "THAT": "4",
    "R0": "0",
    "R1": "1",
    "R2": "2",
    "R3": "3",
    "R4": "4",
    "R5": "5",
    "R6": "6",
    "R7": "7",
    "R8": "8",
    "R9": "9",
    "R10": "10",
    "R11": "11",
    "R12": "12",
    "R13": "13",
    "R14": "14",
    "R15": "15",
    "SCREEN": "16384",
    "KBD": "24576",
}

LABEl = {}
labelValue = 0
# process source file, de-space, de-comment
for line in fileHandle:
    line = line.replace(' ', '').lstrip().rstrip()
    if line.startswith("//") or not line:
        continue
    if "//" in line:
        line = line.split("//")[0]
    if line.startswith('('):
        LABEl[line[1:-1]] = labelValue
        continue
    fileLines.append(line)
    labelValue += 1


def a_instruction(ins):
    content = ins[1:]
    if content.isdigit():
        number = int(content)
        return "0" + "{0:015b}".format(number)
    elif content in LABEl:
        return "0" + "{0:015b}".format(int(LABEl[content]))
    else:
        if content in SYMBOL:
            return "0" + "{0:015b}".format(int(SYMBOL[content]))
        else:
            SYMBOL[content] = str(len(SYMBOL) - 7)
            print(SYMBOL[content])
            return "0" + "{0:015b}".format(int(SYMBOL[content]))


def c_instruction(ins):
    if '=' in ins:
        instruction = ins.split('=')
        return "111" + COMP[instruction[1]] + DEST[instruction[0]] + "000"
    else:
        instruction = ins.split(';')
        return "111" + COMP[instruction[0]] + "000" + JUMP[instruction[1]]


# new destination file
newFile = fileName.split('.')[0] + ".hack"
newFileHandle = open(newFile, 'w')

for line in fileLines:
    if line.startswith('@'):
        newFileHandle.write(a_instruction(line) + '\n')
    else:
        newFileHandle.write(c_instruction(line) + '\n')

fileHandle.close()
newFileHandle.close()
