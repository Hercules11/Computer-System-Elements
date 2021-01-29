import sys
import random


fileName = sys.argv[1]
newFileName = fileName.split('.')[0] + ".asm"

fileHandle = open(fileName, 'r')
newFileHandle = open(newFileName, 'w')

fileContent = []
for line in fileHandle:
    line = line.rstrip().lstrip()
    if line.startswith("//") or not line:
        continue
    if "//" in line:
        line = line.split("//")[0].rstrip()
    fileContent.append(line)

SEGMENT = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

TEMP = {
    "0": "THIS",
    "1": "THAT",
    "eq": "JEQ",
    "gt": "JGT",
    "lt": "JLT"
}


def makelabel():
    return "label" + str(random.randint(0, 100000000))


def vmtrans(ins):
    insArray = ins.split()
    if len(insArray) == 3:
        if insArray[0] == "push":
            if insArray[1] == "constant":
                return f"@{insArray[2]}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D"
            elif insArray[1] in SEGMENT:
                return f"@{insArray[2]}\nD=A\n@{SEGMENT[insArray[1]]}\nA=D+M\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D"
            elif insArray[1] == "static":
                filename = fileName.split('.')[0].split('\\')[-1]
                address = filename + '.' + insArray[2]
                return f"@{address}\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D"
            elif insArray[1] == "temp":
                return f"@{insArray[2]}\nD=A\n@5\nA=D+A\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D"
            elif insArray[1] == "pointer":
                return f"@{TEMP[insArray[2]]}\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D"
        elif insArray[0] == "pop":
            if insArray[1] in SEGMENT:
                return f"@{insArray[2]}\nD=A\n@{SEGMENT[insArray[1]]}\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D"
            elif insArray[1] == "static":
                filename = fileName.split('.')[0].split('\\')[-1]
                address = filename + '.' + insArray[2]
                return f"@SP\nAM=M-1\nD=M\n@{address}\nM=D"
            elif insArray[1] == "temp":
                return f"@{insArray[2]}\nD=A\n@5\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D"
            elif insArray[1] == "pointer":
                return f"@{TEMP[insArray[2]]}\nD=A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D"
        elif insArray[0] == "function":
            localHead = makelabel()
            localTail = makelabel()
            if insArray[1] == "Sys.init":
                return f"@256\nD=A\n@SP\nM=D\n@Sys.init\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" \
                       f"@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" \
                       f"@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@5\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n" \
                       f"@SP\nD=M\n@LCL\nM=D\n@Sys.init\n0;JMP\n(Sys.init)"
            return f"({insArray[1]})\n@SP\nD=M\n@LCL\nM=D\n@{insArray[2]}\nD=A\n" \
                   f"({localHead})\n@{localTail}\nD;JEQ\nD=D-1\n@SP\nAM=M+1\nA=A-1\nM=0\n@{localHead}\n0;JMP\n({localTail})"
        elif insArray[0] == "call":
            argHead = makelabel()
            argTail = makelabel()
            instanceLabel = makelabel()
            return f"@{instanceLabel}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" \
                   f"@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" \
                   f"@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@5\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n" \
                   f"@{insArray[2]}\nD=A\n({argHead})\n@{argTail}\nD;JEQ\nD=D-1\n@ARG\nM=M-1\n@{argHead}\n0;JMP\n({argTail})\n" \
                   f"@SP\nD=M\n@LCL\nM=D\n@{insArray[1]}\n0;JMP\n({instanceLabel})"
    elif len(insArray) == 1:
        if insArray[0] == "add":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M"
        elif insArray[0] == "sub":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D"
        elif insArray[0] == "neg":
            return f"@SP\nA=M-1\nM=-M"
        elif insArray[0] in TEMP:
            compareLabelHead = makelabel()
            compareLabelTail = makelabel()
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@{compareLabelHead}\nD;{TEMP[insArray[0]]}\n" \
                   f"@SP\nA=M-1\nM=0\n@{compareLabelTail}\n0;JMP\n({compareLabelHead})\n@SP\nA=M-1\nM=-1\n({compareLabelTail})"
        elif insArray[0] == "and":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M"
        elif insArray[0] == "or":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M"
        elif insArray[0] == "not":
            return f"@SP\nA=M-1\nM=!M"
        elif insArray[0] == "return":
            return f"@LCL\nD=M\n@R13\nM=D\n@5\nD=A\n@R13\nA=M-D\nD=M\n@R14\nM=D\n@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n" \
                   f"@R13\nAM=M-1\nD=M\n@THAT\nM=D\n@R13\nAM=M-1\nD=M\n@THIS\nM=D\n@R13\nAM=M-1\nD=M\n@ARG\nM=D\n" \
                   f"@R13\nAM=M-1\nD=M\n@LCL\nM=D\n@R14\nA=M\n0;JMP"
    elif len(insArray) == 2:
        if insArray[0] == "label":
            return f"({insArray[1]})"
        elif insArray[0] == "goto":
            return f"@{insArray[1]}\n0;JMP"
        elif insArray[0] == "if-goto":
            return f"@SP\nAM=M-1\nD=M\n@{insArray[1]}\nD;JNE"


for line in fileContent:
    newFileHandle.write(vmtrans(line) + '\n')

fileHandle.close()
newFileHandle.close()
