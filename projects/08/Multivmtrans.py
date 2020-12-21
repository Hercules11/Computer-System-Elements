import os
import sys

folderName = sys.argv[1]
files = []
for file in os.listdir(folderName):
    if file.endswith(".vm"):
        file = folderName + '\\' + file
        files.append(file)

for file in files:
    os.system(f"python vmtrans.py {file}")


newFileName = folderName + '\\' + folderName.split('\\')[-1] + ".asm"
newFileHandle = open(newFileName, 'a')

for file in os.listdir(folderName):
    if file.endswith("Sys.asm"):
        file = folderName + '\\' + file
        initFile = open(file, 'r')
        newFileHandle.write(initFile.read())
        initFile.close()
        os.remove(file)

for file in os.listdir(folderName):
    if file.endswith(".asm") and not file.endswith("Sys.asm"):
        file = folderName + '\\' + file
        addFile = open(file, 'r')
        newFileHandle.write(addFile.read())
        addFile.close()
        if file == newFileName:
            continue
        os.remove(file)
newFileHandle.close()
