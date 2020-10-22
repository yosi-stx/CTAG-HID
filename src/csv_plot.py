#!/usr/bin/python3

from warnings import filterwarnings
filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
import matplotlib.pyplot as plt
import numpy as np
import csv
from ctag_hid_log_files_path import *
import argparse

_MAX_VAL = 4000

def csv_to_numpy_int_array(file):
    reader = csv.reader(file, delimiter=",")
    data = np.array([[st.strip(" ") for st in li] for li in list(reader)]).astype(int)
    return data

def plot(file1, file2, file3):
    # Create a figure and axes
    fig, ax = plt.subplots()

    # Get the array from the csv
    a = csv_to_numpy_int_array(file1)
    b = csv_to_numpy_int_array(file2)
    s = csv_to_numpy_int_array(file3)

    x1 = len(a) # The number of elements in the 1st dimension (number of rows)
    x2 = 10 * x1

    # Plot "a"
    xa = a[:, 0] - (a[0, 0] - 1) # Start the indices from 1
    xa = 10 * xa - 9
    ax.plot(xa[0:x1], a[0:x1, 1], "o-r")

    # Plot "b"
    last_b_index = len(b) # The number of elements in the 1st dimension (number of rows)
    xb = np.arange(1, last_b_index + 1) # Start the indices from 1
    ax.plot(xb[0:x2], b[0:x2, 1], "*-b")

    # Plot the clicks
    c = b[:, 2] # The clicks counter
    c = np.diff(c) # Diff the click counter (1 only where there's a click)
    c = c * _MAX_VAL # Scale the clicks
    ax.plot(c, "o-", c="magenta")

    # Plot the clicker_sound
    ax2 = ax.twinx()
    ax2.plot(s, "o-", c="lime")

    # Show the graphs
    plt.show()

def main():
    parser=argparse.ArgumentParser(
        description='''Plots recording graph after executing: ctag_hid_GUI_less_clicker_rec_Graph . ''',
        epilog="""End of plotting.""")
    args = parser.parse_args()
    file1 = None
    file2 = None
    file3 = None
    try:
        file1 = open(FILE1_PATH,"r")
        file2 = open(FILE2_PATH,"r")
        file3 = open(FILE3_PATH,"r")
        # Plot the graphs
        plot(file1, file2, file3)
    finally:
        if file1 != None:
            file1.close()
        if file2 != None:
            file2.close()
        if file3 != None:
            file3.close()

if __name__ == "__main__":
    main()