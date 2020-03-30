#!/usr/bin/python3

import os

# Put the DLL either in X86_DLL or X64_DLL dirs, or in the same directory as the python script
X86_DLL = "x86"
X64_DLL = "x64"
X86_DLL_BACK = "../x86"
X64_DLL_BACK = "../x64"

def load_dll_path():
    import os
    from platform import architecture

    dll_path = None
    dll_path_back = None
    arch = architecture()[0]
    if arch == "64bit":
        dll_path = X64_DLL
        dll_path_back = X64_DLL_BACK
    elif arch == "32bit":
        dll_path = X86_DLL
        dll_path_back = X86_DLL_BACK
    else:
        raise Exception("Unsupported architecture (not x86 or x64)")
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dll_path = os.path.abspath(os.path.join(file_path, dll_path))
    dll_path_back = os.path.abspath(os.path.join(file_path, dll_path_back))
    env_path = ";".join((file_path, dll_path, dll_path_back, os.environ["PATH"]))
    os.environ["PATH"] = env_path

load_dll_path()