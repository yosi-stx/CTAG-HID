#!/usr/bin/python3

import sys
import multiprocessing as mp
from queue import Queue
from timeit import default_timer as timer
from time import sleep
import pyaudio as pa
import struct
from ctag_hid_log_files_path import *


_RATE = 5000 # Sample once every 0.2 ms
_CHUNK = _RATE # Read chunks of 2 ms each
_FORMAT = pa.paInt16
_CHANNELS = 1
_CHUNK_TIME = _CHUNK / _RATE
_FORMAT_MAX_VAL = 65536

_MAX_VAL = 4000

_DATA_OFFSET = _MAX_VAL / 2
_DATA_AMPLIFY = 20.0

_start_event = None # Synchronizes the recording process
_end_event = None # Synchronizes the read callback thread

_mgr = None # Manages the shared variables between processes
_ns = None # Shared variables between processes

_rec_proc = None
_queue = None

def _record_callback(in_data, frame_count, time_info, status_flags):
    # print("time_info=" + repr(time_info))
    global _ns
    curr_time = timer()
    # print("Debug")
    if _start_event.is_set():
        # print("Debug IN")
        # print("start_time=%f" % (_ns.start_time))
        # print("last_time=%f" % (_ns.last_time))
        time_offset = max(_ns.start_time - _ns.last_time, 0)
        buffer_percent = time_offset / _CHUNK_TIME
        buffer_idx = int(buffer_percent * _CHUNK)
        data_int = struct.unpack("%dh" % (_CHUNK), in_data)
        buffer_end = len(data_int)
        if _end_event.is_set():
            # print("end_time=%f" % (_ns.end_time))
            buffer_end_percent = (curr_time - _ns.end_time) / _CHUNK_TIME
            buffer_end = int(1 + buffer_end_percent * _CHUNK)
        # print("len(data_int)=%d" % (len(data_int[buffer_idx:buffer_end])))
        # map(_queue.put, data_int[buffer_idx:buffer_end])
        for d in data_int:
            _queue.put(d)

    stat = pa.paContinue
    if _end_event.is_set():
        _queue.put(None)
        stat = pa.paComplete
    _ns.last_time = curr_time
    return (None, stat)

def _data_func(data):
    data = data / _FORMAT_MAX_VAL # Scale from -0.5 to 0.5
    data = max(min(data * _DATA_AMPLIFY, 0.5), -0.5) # Amplify and cap to between -0.5 to 0.5
    data = data * _MAX_VAL # Scale to the graph max value (signed)
    data = data + _DATA_OFFSET # Align the data to the middle of the graph (unsigned)
    data = int(data) # Return it as integer
    return data

def _record_func(init_event, start_event, end_event, ns):
    global _start_event
    global _end_event
    global _ns
    _start_event = start_event
    _end_event = end_event
    _ns = ns

    pa_dev = pa.PyAudio()
    pa_stream = pa_dev.open(
        format=_FORMAT,
        channels=_CHANNELS,
        rate=_RATE,
        input=True,
        frames_per_buffer=_CHUNK,
        stream_callback=_record_callback
    )
    # print("latency=%f" % (pa_stream.get_input_latency()))
    global _queue
    _queue = Queue()
    pa_stream.start_stream()
    _ns.init_time = timer()
    _ns.last_time = _ns.init_time
    init_event.set()

    _start_event.wait() # Wait for _start_event to start recording into a file

    file3 = open(FILE3_PATH, "w")
    data = _queue.get()
    while data != None:
        L3 = [ str(_data_func(data)), "\n" ]
        file3.writelines(L3)
        data = _queue.get()

    pa_stream.stop_stream()
    pa_stream.close()
    pa_dev.terminate()

def start_recording():
    if not _start_event.is_set():
        # print("start_event set")
        _ns.start_time = timer()
        _start_event.set()

def stop():
    if not _end_event.is_set():
        # print("end_event set")
        _ns.end_time = timer()
        _end_event.set()

def join():
    global _rec_proc
    if _rec_proc != None:
        # print("rec_proc join")
        _rec_proc.join()
        _rec_proc = None

def init():
    global _rec_proc
    if _rec_proc == None:
        global _start_event
        global _end_event
        global _mgr
        global _ns
        _mgr = mp.Manager()
        _ns = _mgr.Namespace()
        _ns.init_time = None
        _ns.last_time = None
        _ns.start_time = None
        _ns.end_time = None
        _start_event = mp.Event() # Synchronizes the recording process
        _end_event = mp.Event() # Synchronizes the read callback thread
        init_event = mp.Event()
        _rec_proc = mp.Process(target=_record_func, args=(init_event, _start_event, _end_event, _ns))
        _rec_proc.start()
        init_event.wait() # Wait for the process to finish initializing