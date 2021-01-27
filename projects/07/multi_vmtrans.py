import sys, os

folderName = sys.argv[1]
files = []
for file in os.listdir(folderName):
    if file.endswith(".vm"):
        file = folderName + '\\' + file
        files.append(file)
for file in files:
    os.system(f"python vmtrans.py {file}")

