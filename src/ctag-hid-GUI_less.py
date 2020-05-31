#!/usr/bin/python3

from binascii import hexlify
import sys
import argparse
import threading
from time import perf_counter as timer


import include_dll_path
import hid

VENDOR_ID = 0x24b3 # Simbionix
PRODUCT_ID = 0x1005 # Simbionix MSP430 Controller
# file1 = None
# open recording log file:
# file1 = open("C:\Work\Python\CTAG_HID\src\log\clicker_log.txt","w") 
# file1 = open("C:\Work\Python\CTAG_HID\src\log\clicker_log.csv","w") 
file1 = open("C:\Work\Python\CTAG_HID\src\log\motor_current.csv","w") 
file2 = open("C:\Work\Python\CTAG_HID\src\log\clicker_overSample.csv","w") 

# full value variables.
DEAD_ZONE_LOWER_THR = 300
DEAD_ZONE_UPPER_THR = 3300
InnerHandleFULLValue = 0
# InnerHandleChannel1 = 0
# InnerHandleChannel2 = 0
prev_int_inner_handle_channel = [5555,5555]
# prev_int_inner_handle_channel2 = 5555
Delta_Inner = 0
Delta_Inner2 = 0
Active_Encoder = 0
Check_Change_Channel = 0


READ_SIZE = 64 # The size of the packet
READ_TIMEOUT = 2 # 2ms

WRITE_DATA = bytes.fromhex("3f3ebb00b127ff00ff00ff00ffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

SLEEP_AMOUNT = 0.002 # Read from HID every 2 milliseconds
PRINT_TIME = 1.0 # Print every 1 second

START_INDEX = 2 + 4 # Ignore the first two bytes, then skip the version (4 bytes)
#ANALOG_INDEX_LIST = list(range(START_INDEX + 2, START_INDEX + 4 * 2 + 1, 2)) + [START_INDEX + 6 * 2,]
#2020_05_28 - for recording of motor current.
ANALOG_INDEX_LIST = list(range(START_INDEX + 2, START_INDEX + 8 * 2 + 1, 2)) 

COUNTER_INDEX = 2 + 22 + 18 # Ignore the first two bytes, then skip XData1 (22 bytes) and OverSample (==XDataSlave1; 18 bytes)
OVER_SAMPLE_INDEX = 2 + 22
OVER_SAMPLE_INDEX_LIST = list(range(OVER_SAMPLE_INDEX, OVER_SAMPLE_INDEX + 9 * 2 + 1, 2))

OUTER_HANDLE_CHANNEL1_STYLE = "OuterHandleChannel1"
OUTER_HANDLE_CHANNEL2_STYLE = "OuterHandleChannel2"
INNER_HANDLE_CHANNEL1_STYLE = "InnerHandleChannel1"
INNER_HANDLE_CHANNEL2_STYLE = "InnerHandleChannel2"
CLICKER_STYLE = "Clicker"

style_names = [
    OUTER_HANDLE_CHANNEL1_STYLE,
    OUTER_HANDLE_CHANNEL2_STYLE,
    INNER_HANDLE_CHANNEL1_STYLE,
    INNER_HANDLE_CHANNEL2_STYLE,
    CLICKER_STYLE
]

progressbar_styles = list()
progressbars = list()
isopen = list()
inner_clicker = list()
red_handle = list()
reset_check = list()
counter_entry = list()

root = None

def update_checkbox(checkbox, bool_value):
    if (bool_value):
        checkbox.select()
    else:
        checkbox.deselect()

def gui_loop(device):
    do_print = True
    print_time = 0.0
    time = timer()
    handle_time = timer()
    write_time_capture = timer()
    skip_write = 0
    prev_counter = 0
    read_cycle_counter = 0
    seconds_counter = 0
    # cnt = None
    # prev_cnt = None
    # value = None
    # vars for full value of encoder.
    global prev_int_inner_handle_channel
    # global prev_int_inner_handle_channel2
    global Delta_Inner
    global Delta_Inner2
    global InnerHandleFULLValue
    global DEAD_ZONE_LOWER_THR
    global DEAD_ZONE_UPPER_THR
    global Active_Encoder
    global Check_Change_Channel


    while True:
        # Reset the counter
        if (do_print):
            print_time = timer()

        # Write to the device (request data; keep alive)
        if (skip_write % 4) == 0:
            skip_write = 0
            device.write(WRITE_DATA)
            write_time = timer() - write_time_capture
            write_time_capture = timer()
            # print("write_time: %.10f" % write_time)
        skip_write += 1
        
        cycle_time = timer() - time
        # print("cycle timer: %.10f" % cycle_time)

        # If not enough time has passed, sleep for SLEEP_AMOUNT seconds
        sleep_time = SLEEP_AMOUNT - (cycle_time)
        # print("sleep timer: %.10f" % sleep_time)
        # if sleep_time > 0.001:
            # # if value:
            # #     prev_cnt = cnt
            # #     cnt = value[COUNTER_INDEX]
            # #     if prev_cnt and cnt < prev_cnt:
            # #         print("Invalid counter")
            
            # print("in sleep: ")
            # # sleep(sleep_time)

        # Measure the time
        time = timer()
        # print(" ")

        # Read the packet from the device
        value = device.read(READ_SIZE, timeout=READ_TIMEOUT)

        # Update the GUI
        if len(value) >= READ_SIZE:
            # save into file:
            digital = (int(value[START_INDEX + 1]) << 8) + int(value[START_INDEX + 0])
            analog = [(int(value[i + 1]) << 8) + int(value[i]) for i in ANALOG_INDEX_LIST]
            OverSample = [(int(value[i + 1]) << 8) + int(value[i]) for i in OVER_SAMPLE_INDEX_LIST]
            MotorCur = analog[4]  # new, after changing indexes.
            clicker_analog = analog[5]
            batteryLevel = analog[7]
            counter = (int(value[COUNTER_INDEX + 1]) << 8) + int(value[COUNTER_INDEX])
            count_dif = counter - prev_counter 
            
            #---------------------------------------------------------------------------------------
            # aggregate handle counts of inner encoder.
            bool_inner_isopen = bool((digital >> 0) & 0x0001)
            bool_outer_isopen = bool((digital >> 1) & 0x0001)
            int_inner_handle_channel = [analog[0],analog[3]]
            # int_inner_handle_channel[1] = analog[3]
            if prev_int_inner_handle_channel[0] == 5555:
                prev_int_inner_handle_channel = [int_inner_handle_channel[0],int_inner_handle_channel[1]]
                Active_Encoder = 0
                # prev_int_inner_handle_channel2 = int_inner_handle_channel[1]
            
            # DEAD_ZONE_LOWER_THR 300
            # DEAD_ZONE_UPPER_THR 3300
            if (bool_inner_isopen != 0):
            # if ( 0 ):
                pass
                InnerHandleFULLValue = 0;
                # print("-",end = " ", flush=True)
            else:
                  # // check if last 2 samples are in the "live zone", 2 samples are needed to check stability 
                  # // (in the dead zone we can get garbage values, which might be in the right range)
                # if int_inner_handle_channel[0] > DEAD_ZONE_LOWER_THR and \
                   # int_inner_handle_channel[0] < DEAD_ZONE_UPPER_THR and \
                   # prev_int_inner_handle_channel[0] > DEAD_ZONE_LOWER_THR and \
                   # prev_int_inner_handle_channel[0] < DEAD_ZONE_UPPER_THR:
                    # Delta_Inner = -(int_inner_handle_channel[0] - prev_int_inner_handle_channel[Active_Encoder])
                    # InnerHandleFULLValue += Delta_Inner
                # else:
                    # Delta_Inner = -(int_inner_handle_channel[1] - prev_int_inner_handle_channel[1])
                    # InnerHandleFULLValue += Delta_Inner

                Delta_Inner = -(int_inner_handle_channel[Active_Encoder] - prev_int_inner_handle_channel[Active_Encoder])
                InnerHandleFULLValue += Delta_Inner

            if( Check_Change_Channel > 0):
                Check_Change_Channel -= 1

            # if( Check_Change_Channel == 0):
            if  int_inner_handle_channel[Active_Encoder] > DEAD_ZONE_LOWER_THR and \
                int_inner_handle_channel[Active_Encoder] < DEAD_ZONE_UPPER_THR and \
                prev_int_inner_handle_channel[Active_Encoder] > DEAD_ZONE_LOWER_THR and \
                prev_int_inner_handle_channel[Active_Encoder] < DEAD_ZONE_UPPER_THR:
                # stay with the active channel
                pass
            else:
                #change Active_Encoder
                if (Active_Encoder == 1):
                    Active_Encoder = 0
                else:
                    Active_Encoder = 1
                # if active channel was change, dont change again for 50 mS (25 cycles)
                Check_Change_Channel = 25

            if InnerHandleFULLValue < 0 :
                InnerHandleFULLValue = 0 

            prev_int_inner_handle_channel[0] = int_inner_handle_channel[0]
            prev_int_inner_handle_channel[1] = int_inner_handle_channel[1]
            #---------------------------------------------------------------------------------------
            
            
            
            
            global file1
            # if count_dif > 1 :
                # L = [ str(counter),",   ", str(clicker_analog), ", " , str(count_dif), " <<<<<--- " ,"\n" ]  
            # else:
                # L = [ str(counter),",   ", str(clicker_analog), ", " , str(count_dif), "\n" ]  
            # L = [ str(counter),",   ", str(MotorCur), ", " , str(InnerHandleFULLValue), "\n" ]  
            # L = [ str(int_inner_handle_channel[1]),",   ", str(int_inner_handle_channel[0]), ", " \
                 # , str(InnerHandleFULLValue),", " , str(Active_Encoder), "\n" ]  
            L = [ str(Delta_Inner),",   ", str(int_inner_handle_channel[0]), ", " \
                 , str(InnerHandleFULLValue),", " , str(Active_Encoder), "\n" ]  
            
            # add the Data.Master.ADC[5] just before the OverSample elements.
            # file2.writelines(L) # commented out on 2020_05_28, for motor current recording.
            for i in range(0,9):
                L2 = [ str(counter),",   ", str(OverSample[i]), ", " , str(count_dif), "\n" ]  
                file2.writelines(L2) 
            file1.writelines(L) 
            # handler(value, do_print=do_print)
            # print("Received data: %s" % hexlify(value))
            Handler_Called = (timer() - handle_time)
            read_cycle_counter += 1
            if read_cycle_counter >= 500 :
                seconds_counter += 1
                read_cycle_counter = 0
                print( str(seconds_counter))
            # if Handler_Called > 0.002 :
                # print("handler called: %.6f" % Handler_Called)
            # print("time: %.6f" % time)
            handle_time = timer() 
            prev_counter = counter

        # Update the do_print flag
        do_print = (timer() - print_time) >= PRINT_TIME

def handler(value, do_print=False):
    if do_print:
        print("Received data: %s" % hexlify(value))

    return # do without gui
    digital = (int(value[START_INDEX + 1]) << 8) + int(value[START_INDEX + 0])
    analog = [(int(value[i + 1]) << 8) + int(value[i]) for i in ANALOG_INDEX_LIST]
    counter = (int(value[COUNTER_INDEX + 1]) << 8) + int(value[COUNTER_INDEX])

    encoder1 = analog[3]
    encoder2 = analog[0]
    encoder3 = analog[1]
    encoder4 = analog[2]
    clicker_analog = analog[5]
    
    # file1 = open("C:\Work\Python\CTAG_HID\src\log\clicker_log.txt","w") 
    global file1
    # L = [ str(clicker_analog), "," ,"\n" ]  
    # file1.writelines(L) 




    bool_inner_isopen = bool((digital >> 0) & 0x0001)
    bool_outer_isopen = bool((digital >> 1) & 0x0001)
    bool_clicker = bool((digital >> 2) & 0x0001)
    bool_reset = bool((digital >> 4) & 0x0001)
    bool_red_handle = bool((digital >> 7) & 0x0001)
    int_outer_handle_channel1 = analog[1]
    int_outer_handle_channel2 = analog[2]
    int_inner_handle_channel1 = analog[0]
    int_inner_handle_channel2 = analog[3]
    int_clicker = clicker_analog
    int_counter = counter
    precentage_outer_handle_channel1 = int((int_outer_handle_channel1 / 4096) * 100)
    precentage_outer_handle_channel2 = int((int_outer_handle_channel2 / 4096) * 100)
    precentage_inner_handle_channel1 = int((int_inner_handle_channel1 / 4096) * 100)
    precentage_inner_handle_channel2 = int((int_inner_handle_channel2 / 4096) * 100)
    precentage_clicker = int((int_clicker / 4096) * 100)

    progressbar_style_outer_handle_channel1 = progressbar_styles[0]
    progressbar_style_outer_handle_channel2 = progressbar_styles[1]
    progressbar_style_inner_handle_channel1 = progressbar_styles[2]
    progressbar_style_inner_handle_channel2 = progressbar_styles[3]
    progressbar_style_clicker = progressbar_styles[4]
    progressbar_outer_handle_channel1 = progressbars[0]
    progressbar_outer_handle_channel2 = progressbars[1]
    progressbar_inner_handle_channel1 = progressbars[2]
    progressbar_inner_handle_channel2 = progressbars[3]
    progressbar_clicker = progressbars[4]
    checkbox_outer_handle_isopen = isopen[0]
    checkbox_inner_handle_isopen = isopen[1]
    checkbox_inner_clicker = inner_clicker
    checkbox_red_handle = red_handle
    checkbox_reset_check = reset_check
    entry_counter = counter_entry

    progressbar_style_outer_handle_channel1.configure(
        OUTER_HANDLE_CHANNEL1_STYLE,
        text=("%d" % int_outer_handle_channel1)
    )
    progressbar_style_outer_handle_channel2.configure(
        OUTER_HANDLE_CHANNEL2_STYLE,
        text=("%d" % int_outer_handle_channel2)
    )
    progressbar_style_inner_handle_channel1.configure(
        INNER_HANDLE_CHANNEL1_STYLE,
        text=("%d" % int_inner_handle_channel1)
    )
    progressbar_style_inner_handle_channel2.configure(
        INNER_HANDLE_CHANNEL2_STYLE,
        text=("%d" % int_inner_handle_channel2)
    )
    progressbar_style_clicker.configure(
        CLICKER_STYLE,
        text=("%d" % int_clicker)
    )

    progressbar_outer_handle_channel1["value"] = precentage_outer_handle_channel1
    progressbar_outer_handle_channel2["value"] = precentage_outer_handle_channel2
    progressbar_inner_handle_channel1["value"] = precentage_inner_handle_channel1
    progressbar_inner_handle_channel2["value"] = precentage_inner_handle_channel2
    progressbar_clicker["value"] = precentage_clicker

    update_checkbox(checkbox_outer_handle_isopen, bool_outer_isopen)
    update_checkbox(checkbox_inner_handle_isopen, bool_inner_isopen)
    update_checkbox(checkbox_inner_clicker, bool_clicker)
    update_checkbox(checkbox_red_handle, bool_red_handle)
    update_checkbox(checkbox_reset_check, bool_reset)

    entry_counter.delete(0, tk.END)
    entry_counter.insert(tk.END, "%d" % int_counter)

    root.update()

PROGRESS_BAR_LEN = 300

def my_channel_row(frame, row, label, style):
    ttk.Label(
        frame,
        text=label
    ).grid(
        row=row,
        sticky=tk.W
    )

    row += 1

    ttk.Label(
        frame,
        text="Is Open"
    ).grid(
        row=row,
        column=0,
        sticky=tk.W
    )
    ttk.Label(
        frame,
        text="Channel 1"
    ).grid(
        row=row,
        column=1
    )
    ttk.Label(
        frame,
        text="Channel 2"
    ).grid(
        row=row,
        column=2
    )

    row += 1

    w = tk.Checkbutton(
        frame,
        state=tk.DISABLED
    )
    isopen.append(w)
    w.grid(
        row=row,
        column=0
    )
    w = ttk.Progressbar(
        frame,
        orient=tk.HORIZONTAL,
        length=PROGRESS_BAR_LEN,
        style=("%sChannel1" % style)
    )
    progressbars.append(w)
    w.grid(
        row=row,
        column=1
    )
    w = ttk.Progressbar(
        frame,
        orient=tk.HORIZONTAL,
        length=PROGRESS_BAR_LEN,
        style=("%sChannel2" % style)
    )
    progressbars.append(w)
    w.grid(
        row=row,
        column=2
    )

    return row + 1

def my_seperator(frame, row):
    ttk.Separator(
        frame,
        orient=tk.HORIZONTAL
    ).grid(
        pady=10,
        row=row,
        columnspan=3,
        sticky=(tk.W + tk.E)
    )
    return row + 1

def my_widgets(frame):
    # Add style for labeled progress bar
    for name in style_names:
        style = ttk.Style(
            frame
        )
        progressbar_styles.append(style)
        style.layout(
            name,
            [
                (
                    "%s.trough" % name,
                    {
                        "children":
                        [
                            (
                                "%s.pbar" % name,
                                {"side": "left", "sticky": "ns"}
                            ),
                            (
                                "%s.label" % name,
                                {"sticky": ""}
                            )
                        ],
                        "sticky": "nswe"
                    }
                )
            ]
        )
        style.configure(name, background="lime")


    # Outer Handle
    row = 0
    row = my_channel_row(
        frame=frame,
        row=row,
        label="Outer Handle",
        style="OuterHandle"
    )

    # Seperator
    row = my_seperator(frame, row)

    # Inner Handle
    row = my_channel_row(
        frame=frame,
        row=row,
        label="Inner Handle",
        style="InnerHandle"
    )

    # Seperator
    row = my_seperator(frame, row)

    # Clicker labels
    ttk.Label(
        frame,
        text="Inner Clicker"
    ).grid(
        row=row,
        column=0,
        sticky=tk.W
    )
    ttk.Label(
        frame,
        text="Clicker"
    ).grid(
        row=row,
        column=1
    )

    row += 1

    # Clicker data
    w = tk.Checkbutton(
        frame,
        state=tk.DISABLED
    )
    global inner_clicker
    inner_clicker = w
    w.grid(
        row=row,
        column=0
    )
    w = ttk.Progressbar(
        frame,
        orient=tk.HORIZONTAL,
        length=PROGRESS_BAR_LEN,
        style="Clicker"
    )
    progressbars.append(w)
    w.grid(
        row=row,
        column=1
    )

    row += 1

    # Seperator
    row = my_seperator(frame, row)

    # Red handle and reset button labels
    ttk.Label(
        frame,
        text="Red Handle"
    ).grid(
        row=row,
        column=0,
        sticky=tk.W
    )
    ttk.Label(
        frame,
        text="Reset Button"
    ).grid(
        row=row,
        column=1
    )

    row += 1

    # Red handle and reset button data
    w = tk.Checkbutton(
        frame,
        state=tk.DISABLED
    )
    global red_handle
    red_handle = w
    w.grid(
        row=row,
        column=0
    )
    w = tk.Checkbutton(
        frame,
        state=tk.DISABLED
    )
    global reset_check
    reset_check = w
    w.grid(
        row=row,
        column=1
    )

    row += 1

    # Seperator
    row = my_seperator(frame, row)

    # Counter
    ttk.Label(
        frame,
        text="Counter"
    ).grid(
        row=row,
        column=0,
        sticky=tk.E,
    )
    w = ttk.Entry(
        frame,
        width=20,
        # state=tk.DISABLED
    )
    global counter_entry
    counter_entry = w
    w.grid(
        padx=10,
        pady=5,
        row=row,
        column=1,
        columnspan=2,
        sticky=tk.W,
    )

def init_parser():
    parser = argparse.ArgumentParser(
        description="Read the HID data from C-TAG.\nIf no argument is given, the program exits."
    )
    parser.add_argument(
        "-v", "--vendor",
        dest="vendor_id",
        metavar="VENDOR_ID",
        type=int,
        nargs=1,
        required=False,
        help="connects to the device with the vendor ID"
    )
    parser.add_argument(
        "-p", "--product",
        dest="product_id",
        metavar="PRODUCT_ID",
        type=int,
        nargs=1,
        required=False,
        help="connects to the device with that product ID"
    )
    parser.add_argument(
        "-a", "--path",
        dest="path",
        metavar="PATH",
        type=str,
        nargs=1,
        required=False,
        help="connects to the device with the given path"
    )
    return parser

def main():
    global VENDOR_ID
    global PRODUCT_ID
    PATH = None
    
    # open recording log file:
    # file1 = open("C:\Work\Python\CTAG_HID\src\log\clicker_log.txt","w") 

    # Parse the command line arguments
    parser = init_parser()
    args = parser.parse_args(sys.argv[1:])

    # Initialize the flags according from the command line arguments
    avail_vid = args.vendor_id != None
    avail_pid = args.product_id != None
    avail_path = args.product_id != None
    id_mode = avail_pid and avail_vid
    path_mode = avail_path
    default_mode = (not avail_vid) and (not avail_pid) and (not avail_path)
    if (path_mode and (avail_pid or avail_vid)):
        print("The path argument can't be mixed with the ID arguments")
        return
    if ((not avail_path) and ((avail_pid and (not avail_vid)) or ((not avail_pid) and avail_vid))):
        print("Both the product ID and the vendor ID must be given as arguments")
        return

    if (default_mode):
        print("No arguments were given, defaulting to:")
        print("VENDOR_ID = %X" % VENDOR_ID)
        print("PRODUCT_ID = %X" % PRODUCT_ID)
        id_mode = True
    elif (id_mode):
        VENDOR_ID = args.vendor_id[0]
        PRODUCT_ID = args.product_id[0]
    elif (path_mode):
        PATH = args.path[0]
    else:
        raise NotImplementedError

    device = None

    try:
        if (id_mode):
            device = hid.Device(vid=VENDOR_ID, pid=PRODUCT_ID)
        elif (path_mode):
            device = hid.Device(path=PATH)
        else:
            raise NotImplementedError

        
        # Create thread that calls
        threading.Thread(target=gui_loop, args=(device,), daemon=True).start()

        input()
    finally:
        global file1
        global file2
        file1.close() #to change file access modes 
        file2.close() #to change file access modes 
        if device != None:
            device.close()

if __name__ == "__main__":
    main()