#!/usr/bin/python3

# Put the DLL either in X86_DLL or X64_DLL dirs, or in the same directory as the python script
X86_DLL = "../x86"
X64_DLL = "../x64"
def load_dll_path():
    import os
    from platform import architecture

    dll_path = None
    arch = architecture()[0]
    if arch == "64bit":
        dll_path = X64_DLL
    elif arch == "32bit":
        dll_path = X86_DLL
    else:
        raise Exception("Unsupported architecture (not x86 or x64)")
    file_path = os.path.abspath(os.path.dirname(__file__))
    dll_path = os.path.abspath(os.path.join(file_path, dll_path))
    env_path = file_path + ";" + dll_path + ";" + os.environ["PATH"]
    os.environ["PATH"] = env_path
load_dll_path()

import hid # Needs to be imported after load_dll_path
from pprint import pprint

VENDOR_ID = 0x24b3 # Simbionix
PRODUCT_ID = 0x1005 # Simbionix MSP430 Controller

READ_SIZE = 64
READ_TIMEOUT = 1000

WRITE_DATA = bytes("0x3f3ebb00b127ff00ff00ff00ffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", encoding="utf-8")
WRITE_TIMEOUT = 1000

def main():

    device = None

    try:

        device = hid.Device(vid=VENDOR_ID, pid=PRODUCT_ID)

        print(f"Device Manufacturer: {device.manufacturer}")
        print(f"Product: {device.product}")
        print(f"Serial Number: {device.serial}")

        # feature_report = device.get_feature_report()
        # pprint(feature_report)

        device.write(WRITE_DATA)

        bytes_read = device.read(size=READ_SIZE, timeout=READ_TIMEOUT)
        pprint(bytes_read)

    finally:
        if device != None:
            device.close()

    pass

if __name__ == "__main__":
    main()