import os
import sys
import subprocess

script_root = os.path.dirname(os.path.realpath(__file__))
working_dir_stack = list()

def pushd(dir):
    global working_dir_stack
    working_dir_stack.append(os.getcwd())
    os.chdir(dir)
    print("Working dir:", os.getcwd())

def popd():
    global working_dir_stack
    os.chdir(working_dir_stack.pop())
    print("Working dir:", os.getcwd())

def shell(command : str, env = os.environ):
    print("Execute:", command)
    subprocess.run(command, shell=True, env=env)

def build_spvgen():
    global script_root
    pushd(script_root)
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
