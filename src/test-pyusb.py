#!/usr/bin/python3

import include_dll_path
# The next library needs the DLLs in PATH so it can load them
import usb
from pprint import pprint

VENDOR_ID = 0x24b3 # Simbionix
PRODUCT_ID = 0x1005 # Simbionix MSP430 Controller

READ_SIZE = 64
READ_TIMEOUT = 1000

WRITE_DATA = bytes("0x3f3ebb00b127ff00ff00ff00ffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", encoding="utf-8")
WRITE_TIMEOUT = 1000

def main():
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device == None:
        raise ValueError("Device not found")

    # Try reseting the device
    device.reset()

    # Setup the device configuration
    device.set_configuration()

    # Get the active configuration from the device
    cfg = device.get_active_configuration()

    # Get the HID interface from the active configuration
    hid_inter = cfg[(0, 0)]

    # Get the IN endpoint
    ep_in = usb.util.find_descriptor(
        hid_inter,
        custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
                usb.util.ENDPOINT_IN
    )

    # Get the OUT endpoint
    ep_out = usb.util.find_descriptor(
        hid_inter,
        custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
                usb.util.ENDPOINT_IN
    )

    # Clear halt
    # ep_out.clear_halt()
    # ep_in.clear_halt()

    # Try reseting the device
    # device.reset()

    # Write data request
    ep_out.write(WRITE_DATA, timeout=WRITE_TIMEOUT)

    # Read data
    data_barr = ep_in.read(READ_SIZE, timeout=READ_TIMEOUT)
    pprint(data_barr)

    pass

if __name__ == "__main__":
    main()