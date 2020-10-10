#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import csv
from ctag_hid_log_files_path import *

def csv_to_numpy_int_array(file):
    reader = csv.reader(file, delimiter=",")
    data = np.array([[st.strip(" ") for st in li] for li in list(reader)]).astype(int)
    return data

def plot(file1, file2):
    # Create a figure and axes
    fig, ax = plt.subplots()

    # Get the array from the csv
    a = csv_to_numpy_int_array(file1)
    b = csv_to_numpy_int_array(file2)

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
    c = b[:, 3] # The clicks counter
    c = np.diff(c) # Diff the click counter (1 only where there's a click)
    c = c * 4000 # Scale the clicks
    ax.plot(c, "o-", c="magenta")

    # Plot the clicker_sound
    s = b[:, 2] # The clicker sound wave
    ax.plot(s, "o-", c="lime")

    # Show the graphs
    plt.show()

def main():
    file1 = None
    file2 = None
    try:
        file1 = open(FILE1_PATH,"r")
        file2 = open(FILE2_PATH,"r")
        # Plot the graphs
        plot(file1, file2)
    finally:
        if file1 != None:
            file1.close()
        if file2 != None:
            file2.close()

if __name__ == "__main__":
    main()