import os
import ctypes
from ctypes import c_char_p

def nullChecker(input_csv, tool=4):

    # Determine the path to the shared library (libFahes.so)
    libfile = os.path.join(os.path.dirname(__file__), "src", "libFahes.so")

    # Set up the output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'Results')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert the input file path to an absolute path
    tName = os.path.abspath(input_csv)

    # Load and configure the shared library
    Fahes = ctypes.CDLL(libfile)
    Fahes.start.restype = None
    Fahes.start.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]

    # Execute the FAHES tool with the specified parameters
    Fahes.start(c_char_p(tName.encode('utf-8')), c_char_p(output_dir.encode('utf-8')), tool)

    # Construct and return the path to the output CSV containing DMVs
    dmvs_csv_name = os.path.join(output_dir, 'DMV_' + os.path.basename(input_csv))
    return dmvs_csv_name

path = './Data/adult.csv'
result = nullChecker(path)

