import sys;
import argparse;
import os;
from fractions import Fraction;

from encoder import HuffmanEncoder;




def getFileSize(filename):
    try:
        size = os.path.getsize(filename); 
        
        if (size < 1000):
            return size, "B"; # Bytes
        elif (size < 1000000):
            return (size / 1000), "KB"; # KiloByte
        else:
            return (size / 1000000), "MB"; # MegaByte
        
    except FileNotFoundError:
        printErrorExit("The file '{}' does not exist".format(filename));
    except IOError:
        printErrorExit("Unabled to access the file '{}'".format(filename));
  
  
def printStatistics(ifile_name, ifile_size, ofile_name, ofile_size, show_compression):
    separator = ("=" * 80);
    section = ("-" * 80);
    
    print(separator);
    print("File Statistics");
    print(separator);
    
    print("Input File");
    print(section);
    print("Name: {0}".format(ifile_name));
    print("File Size: {0:.2f} {1}".format(ifile_size[0], ifile_size[1]));
    print();
    
    print("Output File");
    print(section);
    print("Name: {0}".format(ofile_name));
    print("File Size: {0:.2f} {1}".format(ofile_size[0], ofile_size[1]));
    
    # Compute the compression percentage
    if (show_compression and ifile_size[0] != 0):
        percent = 100 * (1 - (ofile_size[0]/ifile_size[0]));
        print("File Compressed: {0:.2f}%".format(percent));
  
  
def printErrorExit(msg, error_code = 2):
    print("[ERROR]:", msg);
    exit(error_code);
    

def createArgParser():
    parser = argparse.ArgumentParser();
    parser.add_argument("input_file", help="Text file to encode or binary file to decode");
    parser.add_argument("-o", "--ofile", help="File the output is written to, overwrites any existing file");
    parser.add_argument("-e", "--encode", help="Encodes the input file using UTF-8", action="store_true");
    parser.add_argument("-d", "--decode", help="Decodes the input file to UTF-8", action="store_true");
    
    return parser;
    

def main():
    
    # Parse the input arguments
    parser = createArgParser();
    args = parser.parse_args();
    
    
    # No output file name given, use a modified version of the input file name
    ofile = args.ofile;
    if (ofile is None):
        ofile = args.input_file;
        ofile = "{}.out".format(os.path.splitext(ofile)[0]);
    
    
    # Get the initial input file size
    ifile_size = getFileSize(args.input_file);
    show_compression = False;
    
    try:
        # Determine if the file should be encoded or decoded
        if (args.encode and args.decode):
            print("Illegal command: Cannot both encode and decode a single file.");
            parser.print_help();
            exit(2);
        elif (args.decode):
            HuffmanEncoder.decodeFile(args.input_file, ofile);
        else:
            HuffmanEncoder.encodeFile(args.input_file, ofile);
            show_compression = True;
            
            
    except FileNotFoundError:
        printErrorExit("The input file '{}' does not exist".format(args.input_file));
    except IOError:
        printErrorExit("Unabled to access the required files");
    except Exception as err:
        printErrorExit("Invalid file format for '{}' :: {}".format(args.input_file, err));
    
    
    # Get the output file size
    ofile_size = getFileSize(ofile);
    
    #Show the resulting file statistics
    printStatistics(args.input_file, ifile_size, ofile, ofile_size, show_compression);
    
    
main();