import sys

# usage example: python vmtrans.py StackArithmetic\StackTest\StackTest.vm
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
        line = line.split("//")[0]
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


def vmtrans(ins):
    insArray = ins.split()
    uniqueLabel = str(id(insArray[0]))
    LABEL0 = uniqueLabel + "tr"
    LABEL1 = uniqueLabel + "fa"
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
        else:
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
    elif len(insArray) == 1:
        if insArray[0] == "add":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M"
        elif insArray[0] == "sub":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D"
        elif insArray[0] == "neg":
            return f"@SP\nA=M-1\nM=-M"
        elif insArray[0] in TEMP:
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@{LABEL0}\nD;{TEMP[insArray[0]]}\n" \
                   f"@SP\nA=M-1\nM=0\n@{LABEL1}\n0;JMP\n({LABEL0})\n@SP\nA=M-1\nM=-1\n({LABEL1})"
        elif insArray[0] == "and":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M"
        elif insArray[0] == "or":
            return f"@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M"
        elif insArray[0] == "not":
            return f"@SP\nA=M-1\nM=!M"


for line in fileContent:
    newFileHandle.write(vmtrans(line) + '\n')

fileHandle.close()
newFileHandle.close()
