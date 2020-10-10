#!/usr/bin/python3
# file: ctag_hid_GUI_less_clicker_rec_Graph.py
from binascii import hexlify
import sys
import argparse
import threading
#from time import perf_counter as timer
from timeit import default_timer as timer
from time import sleep
import pyaudio as pa
from queue import Queue
import csv_plot
from ctag_hid_log_files_path import *


import include_dll_path
import hid
import os

VENDOR_ID = 0x24b3 # Simbionix
PRODUCT_ID = 0x1005 # Simbionix MSP430 Controller
# file1 = None
# open recording log file:
if not os.path.exists('log'):
    os.makedirs('log')
# file1 = open("C:\Work\Python\CTAG_HID\src\log\clicker_log.txt","w") 
#file1 = open("C:\Work\Python\CTAG_HID\src\log\clicker_log.csv","w") 
#file2 = open("C:\Work\Python\CTAG_HID\src\log\clicker_overSample.csv","w") 
file1 = open(FILE1_PATH,"w") 
file2 = open(FILE2_PATH,"w") 

# PyAudio constants
PA_READ_CHUNK = 200
PA_FRAMES_PER_BUFFER = 200
PA_FORMAT = pa.paInt16
PA_FORMAT_LEN = int(16 / 8) # 2 bytes each
PA_FORMAT_MAX_VAL = 65536
PA_CHANNELS = 1
PA_RATE = 10000 # Every 0.1 ms
# PA_INITIAL_SLEEP = 0.002 # Sleep for 2 ms after starting the stream
# PA_LONG_RECORDING = 0.001 # The recording took a long time
# PA_IN_DATA_INDEX = -2 # The last two bytes (2 samples each 2 bytes (paInt16))

GRAPH_MAX_VAL = 4000

CLICKER_SOUND_OFFSET = GRAPH_MAX_VAL / 2
CLICKER_SOUND_AMPLIFY = 20.0

READ_SIZE = 64 # The size of the packet
READ_TIMEOUT = 2 # 2ms

WRITE_DATA = bytes.fromhex("3f3ebb00b127ff00ff00ff00ffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

SLEEP_AMOUNT = 0.002 # Read from HID every 2 milliseconds
PRINT_TIME = 1.0 # Print every 1 second

START_INDEX = 2 + 4 # Ignore the first two bytes, then skip the version (4 bytes)
#ANALOG_INDEX_LIST = list(range(START_INDEX + 2, START_INDEX + 4 * 2 + 1, 2)) + [START_INDEX + 6 * 2,]
#2020_09_24 - for recording of clickerRec P5.0 .
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
prev_clicker_counter = 0
from_zero_clicker_counts = 0

class DummyQueue:
    def __init__(self, val):
        self._val = val
    def get(self):
        return self._val

# PyAudio objects
pa_dev = None # The PyAudio device
pa_stream = None # The PyAudio input stream
# pa_in_data = [0] * PA_READ_CHUNK # The input data read every 2 ms
pa_in_data = DummyQueue(0) # Dummy queue that returns 0

root = None

pa_callback_rec_start = None
def pa_callback(in_data, frame_count, time_info, status_flags):
    global pa_callback_rec_start
    if pa_callback_rec_start != None:
        time = timer() - pa_callback_rec_start
        # if time > 0.021:
        #     print("pa_callback took too long: %f" % (time))
    global pa_in_data
    if isinstance(pa_in_data, DummyQueue):
        pa_in_data = Queue(3 * PA_READ_CHUNK)
    # li = [None] * PA_READ_CHUNK
    for i in range(PA_READ_CHUNK):
        data = int.from_bytes(
            bytes=in_data[(i * PA_FORMAT_LEN):((i + 1) * PA_FORMAT_LEN)],
            byteorder=sys.byteorder,
            signed=True
        )
        data = data / PA_FORMAT_MAX_VAL # Scale from 0.0 to 1.0
        data = min(data * CLICKER_SOUND_AMPLIFY, 1.0) # Amplify and cap to 1.0
        data = data * GRAPH_MAX_VAL / 2 # Scale to the graph max value (signed)
        data = data + CLICKER_SOUND_OFFSET # Align the data to the middle of the graph (unsigned)
        data = int(data) # Return it as integer
        # li[i] = data
        pa_in_data.put(data)
    # pa_in_data = int.from_bytes(bytes=in_data[:], byteorder=sys.byteorder, signed=True)
    # pa_in_data = li
    pa_callback_rec_start = timer()
    return (None, pa.paContinue) # Required return format of input callback

def update_checkbox(checkbox, bool_value):
    if (bool_value):
        checkbox.select()
    else:
        checkbox.deselect()

clicker_sound_index = 0
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

    global clicker_sound_index
    curr_thrd = threading.current_thread()
    while getattr(curr_thrd, "do_run", True):
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
            analog = [(int(value[i + 1]) << 8) + int(value[i]) for i in ANALOG_INDEX_LIST]
            OverSample = [(int(value[i + 1]) << 8) + int(value[i]) for i in OVER_SAMPLE_INDEX_LIST]
            MotorCur = analog[4]  # new, after changing indexes.
            clicker_analog = analog[5]
            clicker_Rec = analog[6]
            batteryLevel = analog[7]
            # Packets Counter
            counter = (int(value[COUNTER_INDEX + 1]) << 8) + int(value[COUNTER_INDEX])
            count_dif = counter - prev_counter 
            clicker_counter = (int(value[COUNTER_INDEX+2 + 1]) << 8) + int(value[COUNTER_INDEX+2])
            global prev_clicker_counter
            global from_zero_clicker_counts
            if prev_clicker_counter == 0:
                prev_clicker_counter = clicker_counter
                first_clicker_counter = clicker_counter
            if prev_clicker_counter != clicker_counter:
                from_zero_clicker_counts = clicker_counter-first_clicker_counter
                # print("clicker: %d" % (clicker_counter-first_clicker_counter))
                print("clicker: %d" % (from_zero_clicker_counts))
                prev_clicker_counter = clicker_counter
            
            # read from microphone signal: (clicker_sound)
            global pa_in_data # Don't write to this variable (not thread safe)
            clicker_sound = pa_in_data # Read the sampled data
            
            global file1
            # if count_dif > 1 :
                # L = [ str(counter),",   ", str(clicker_analog), ", " , str(count_dif), " <<<<<--- " ,"\n" ]  
            # else:
                # L = [ str(counter),",   ", str(clicker_analog), ", " , str(count_dif), "\n" ]  
            # L = [ str(counter),",   ", str(clicker_analog), ", " , str(count_dif),", " , str(from_zero_clicker_counts), "\n" ]  
            # L = [ str(counter),",   ", str(clicker_analog), ", " , str(clicker_Rec),", " , str(from_zero_clicker_counts), "\n" ]  
            L = [ str(counter),",   ", str(clicker_analog), ", " , str(clicker_sound.get()),", " , str(from_zero_clicker_counts), "\n" ]  
            
            # add the Data.Master.ADC[5] just before the OverSample elements.
            file2.writelines(L) 
            for i in range(0,9):
                # L2 = [ str(counter),",   ", str(OverSample[i]), ", " , str(count_dif),", " , str(from_zero_clicker_counts), "\n" ]  
                # L2 = [ str(counter),",   ", str(OverSample[i]), ", " , str(clicker_Rec),", " , str(from_zero_clicker_counts), "\n" ]  
                L2 = [ str(counter),",   ", str(OverSample[i]), ", " , str(clicker_sound.get()),", " , str(from_zero_clicker_counts), "\n" ]  
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

        # Increment the gui loop iteration counter
        clicker_sound_index += 10
        if clicker_sound_index >= PA_READ_CHUNK:
            clicker_sound_index = 0

def handler(value, do_print=False):
    if do_print:
        print("Received data: %s" % hexlify(value))

    return # do without gui
    digital = (int(value[START_INDEX + 1]) << 8) + int(value[START_INDEX + 0])
    analog = [(int(value[i + 1]) << 8) + int(value[i]) for i in ANALOG_INDEX_LIST]
    # Packets Counter
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
        global pa_dev
        global pa_stream
        pa_dev = pa.PyAudio()
        pa_stream = pa_dev.open(
            format=PA_FORMAT,
            channels=PA_CHANNELS,
            rate=PA_RATE,
            input=True,
            frames_per_buffer=PA_FRAMES_PER_BUFFER,
            stream_callback=pa_callback
        )
        pa_stream.start_stream()
        # sleep(PA_INITIAL_SLEEP) # Sleep for 2 ms

        if (id_mode):
            device = hid.Device(vid=VENDOR_ID, pid=PRODUCT_ID)
        elif (path_mode):
            device = hid.Device(path=PATH)
        else:
            raise NotImplementedError

        
        # Create thread that calls
        thrd = threading.Thread(target=gui_loop, args=(device,), daemon=True)
        thrd.start()

        input()

        thrd.do_run = False # Signal the thread to stop
        thrd.join() # Wait for the thread to stop
    except Exception as err:
        print(err)
        sys.exit(1)
    finally:
        global file1
        global file2
        file1.close() #to change file access modes 
        file2.close() #to change file access modes 
        try:
            if device != None:
                device.close()
            if pa_stream != None:
                pa_stream.stop_stream() # Stop recording
                pa_stream.close() # Terminate the stream
            if pa_dev != None:
                pa_dev.terminate() # Terminate PyAudio
        except Exception as err:
            print(err)

    csv_plot.main()

if __name__ == "__main__":
    main()