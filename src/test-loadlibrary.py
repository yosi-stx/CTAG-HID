#!/usr/bin/python3

import os
import ctypes
from pprint import pprint
from platform import architecture

X86_DLL = "../x86"
X64_DLL = "../x64"

def main():

    dll_path = None
    if architecture()[0] == "64bit":
        dll_path = X64_DLL
    else:
        dll_path = X86_DLL
    dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), dll_path))
    env_path = dll_path + ";" + os.environ["PATH"]
    os.environ["PATH"] = env_path

    hidapi = None
    library_paths = (
        'libhidapi-hidraw.so',
        'libhidapi-hidraw.so.0',
        'libhidapi-libusb.so',
        'libhidapi-libusb.so.0',
        'libhidapi-iohidmanager.so',
        'libhidapi-iohidmanager.so.0',
        'libhidapi.dylib',
        'hidapi.dll',
        'libhidapi-0.dll'
    )

    for lib in library_paths:
        try:
            hidapi = ctypes.cdll.LoadLibrary(lib)
            break
        except OSError:
            pass
    else:
        error = "Unable to load any of the following libraries:{}"\
            .format(' '.join(library_paths))
        raise ImportError(error)

    pprint(hidapi)

    pass

if __name__ == "__main__":
    main()