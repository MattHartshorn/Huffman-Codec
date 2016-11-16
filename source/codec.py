import sys;
import argparse;



def main():
    
    parser = argparse.ArgumentParser();
    parser.add_argument("input_file", help="text file to encode or binary file to decode");
    parser.add_argument("-o", "--ofile", help="file the output is written to, replaces any existing file");
    parser.add_argument("-e", "--encode", help="switches the usage mode to encode the input file", action="store_true");
    parser.add_argument("-d", "--decode", help="switches the usage mode to decode the input file", action="store_true");

    args = parser.parse_args();

    

    
main();