import os
import sys
import subprocess

scriptRoot = os.path.dirname(os.path.realpath(__file__))
workingDirStack = list()

def pushd(dir):
    global workingDirStack
    workingDirStack.append(os.getcwd())
    os.chdir(dir)
    print("Working dir:", os.getcwd())

def popd():
    global workingDirStack
    os.chdir(workingDirStack.pop())
    print("Working dir:", os.getcwd())

def shell(command : str):
    print("Execute:", command)
    subprocess.run(command, shell=True)

def build_spvgen():
    global scriptRoot
    pushd(scriptRoot)
    pushd("external/")
    shell("python fetch_external_sources.py")
    popd()
    shell("cmake -S . -B build")
    shell("cmake --build build/ --target spvgen --config Release")
    popd()

def main() -> int:
    try:
        build_spvgen()
        return 0
    except Exception as e:
        print(e)
        return -1

if __name__ == '__main__':
    sys.exit(main())
