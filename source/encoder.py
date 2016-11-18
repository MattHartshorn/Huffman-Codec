import queue;
import struct;
import codecs;

from node import HuffmanNode;
from fcpair import FrequencyCharPair;


# Endianness of the encoding/decoding process
_BITORDER = 'little';

# FrequencyCharPair that is used to denote the end of the binary data
_TERMINATOR = FrequencyCharPair(0, None);


#==============================================================================
#                             Public Methods
#==============================================================================

def encode(data, ofile_name = None):

    # Declare and open the output file if provided
    ofile = None;
    if (ofile_name is not None):
        ofile = open(ofile_name, "wb+");

    # Compute the character/frequency listing
    fc_pairs = _getFrequencyCharPairs(data);
    
    # Compute the tree and the associated binary map to help form the encoded data
    tree = _createTree(fc_pairs);
    binary_map = _getBinaryMap(tree);
    
    # Encode all the data
    header_buffer = _encodeFrequencyCharPairs(fc_pairs);
    data_buffer = _encodeData(data, binary_map);
    
    if (ofile is not None):
        # Write the data to the output file
        ofile.write(header_buffer);
        ofile.write(data_buffer);
        ofile.close(); 
    else:  
        # Combine and return the byte data
        return _combineEncodedData(header_buffer, data_buffer);
    
def decode(bytes, ofile_name = None):

    # Declare and open the output file if provided
    ofile = None;
    if (ofile_name is not None):
        ofile = codecs.open(ofile_name, "w+", "utf-8");

    # Unpack the header data
    char_byte_count, freq_count, freq_byte_count = struct.unpack_from(_modifyTypeFormat("IIB"), bytes, 0);
    offset = 9;
    
    # Get and decode the frequencies
    freq_buffer = bytes[offset:offset + (freq_count * freq_byte_count)];
    offset += (freq_count * freq_byte_count);
    frequencies = _decodeFrequencies(freq_buffer, freq_byte_count);
    
    # Get and decode the character array
    char_buffer = bytes[offset:offset + char_byte_count];
    offset += char_byte_count;
    fc_pairs = _decodeFrequencyCharPairs(char_buffer, frequencies);
   
    # Create the huffman tree and decode the data
    tree = _createTree(fc_pairs);
    decoded_data = _decodeDataBytes(bytes[offset:], tree);
    
    # Write or return the data
    if (ofile is not None):
        ofile.write(decoded_data);
        ofile.close();
    else:
        return decoded_data;

        
def encodeFile(ifile_name, ofile_name = None):

    ifile = codecs.open(ifile_name, "r", "utf-8");
    data = ifile.read();
    ifile.close();

    bytes = encode(data, ofile_name);
    
    return bytes;
    
def decodeFile(ifile_name, ofile_name = None):

    ifile = open(ifile_name, "rb");
    bytes = ifile.read();
    ifile.close();

    data = decode(bytes, ofile_name);
    
    return data;

    
#==============================================================================    
#                             Private Methods
#==============================================================================

def _createTree(frequency_char_pairs):
    """
    Creates the Huffman Tree used to encode/decode the data.
    
    @param frequency_char_pairs: list of FrequencyCharPairs used to create the tree
    
    @return: returns the tree structure made up of HuffmanNodes and FrequencyCharPairs
    """

    heap = queue.PriorityQueue();
    
    # Place all the frequencies and characters into the heap
    for pair in frequency_char_pairs:
        heap.put(pair);
       
    while (heap.qsize() > 1):
        # Get the left and right items
        left = heap.get();
        right = heap.get();
        
        # Compute the sum of the frequencies and create a node of the combined data
        sum_freq = left.frequency + right.frequency;
        tree_node = HuffmanNode(sum_freq, left, right);

        # Insert the new sub-tree into the heap
        heap.put(tree_node);
        
    # Return the root element which forms the tree
    return heap.get();
    
    
# Decoding 
def _decodeFrequencyCharPairs(char_buffer, frequencies):
    """
    Decodes the character buffer and creates the FrequencyCharPair list.
    
    @param char_buffer: byte array of all the character data, in sorted order by frequency
    @param frequencies: list of all the frequencies in sorted order
    
    @return: the decoded FrequencyCharPair list
    """
    chars = char_buffer.decode("utf-8");

    # Determine if the lengths match
    if (len(chars) != len(frequencies)):
        raise ValueError("The length of the character array and frequencies dont match");

    # Combine the arrays into a tuple array
    res = [];
    for i in range(0, len(chars)):
        res.append(FrequencyCharPair(frequencies[i], chars[i]));
    
    return _formatFrequencyCharPairs(res, False);
    
def _decodeFrequencies(freq_buffer, freq_byte_count):
    """
    Decodes the frequency buffer into a list of frequencies.
    
    @param freq_buffer: the byte array of all the frequencies
    @param freq_byte_count: the number of bytes per frequency
    
    @return: the list of frequencies
    """

    # Invalid input
    if (freq_byte_count <= 0 or freq_byte_count > 4):
        raise ValueError("Invalid frequency byte count, must be greater than zero and less than or equal to 4");
    elif (len(freq_buffer) % freq_byte_count != 0):
        raise ValueError("Invalid length for the frequency buffer, must be a multiple of " + freq_byte_count);
        
    res = [];
    
    # Loop over all the frequencies
    for i in range(0, len(freq_buffer), freq_byte_count):
    
        bytes = freq_buffer[i:i + freq_byte_count];
    
        # Unpack the frequency value
        res.append(_convertBytesToInt(bytes));
        
    return res;

def _decodeDataBytes(data_bytes, tree_root):
    """
    Decodes the main data of the file back into an uncompressed string.
    
    @param data_bytes: compressed data as byte array
    @param tree_root: the root of the Huffman Tree
    
    @return: returns the decoded data as a string
    """

    # Check for empty tree
    if (tree_root is None and data_bytes is not None):
        raise ValueError("tree is empty");
    
    # Check if the data bytes value is valid
    if (data_bytes is None):
        raise ValueError("data_bytes cannot be None");
    elif (len(data_bytes) == 0):
        return "";


    # Initialize the result value and the sub_tree container to the root node
    res = "";
    node = tree_root;
    
    for byte in data_bytes:
        bit = 0;
    
        while (True):
            if (isinstance(node, HuffmanNode)):
                # Non-leaf, traverse left or right and increment bit 
                bit_val = _getBit(byte, bit);
                bit += 1;
                
                if (bit_val):
                    node = node.rightChild;
                else:
                    node = node.leftChild;
            elif (node.character is None):
                return res;
            else:
                # Add the leaf character value, and reset the tree to the head
                res += node.character;
                node = tree_root;
        
        
            # Fetch next byte
            if (bit == 8):
                break;
    
    return res;

    
# Encoding
def _getFrequencyCharPairs(data):
    """
    Retrieves a list of FrequencyCharPair based on the input data.
    
    @param data: the unencoded input data string
    
    @returns: list of FrequencyCharPairs
    """
    
    # Map all the frequencies to their characters
    dict = {};
    for char in data:
        if (char in dict):
            dict[char] = dict[char] + 1;
        else:
            dict[char] = 1;
    
    # Create a list of the key, value pairs from the dictionary
    res = [];
    for char, frequency in dict.items():
        res.append(FrequencyCharPair(frequency, char));
    
    #return res;
    return _formatFrequencyCharPairs(res, True);

def _getBinaryMap(tree_root):
    bin_map = {};
    
    # Create the stack to house the nodes
    stack = [];
    stack.append((tree_root, ""));
    
    while (stack):
        
        # Get the top item and discard the frequency summation
        node, bit_str = stack.pop();
        
        if (isinstance(node, HuffmanNode)):
            # Add the child nodes to the stack
            stack.append((node.rightChild, bit_str + "1"));
            stack.append((node.leftChild, bit_str + "0"));
        else:
            # Leaf Node, map the binary string to the character
            bin_map[node.character] = bit_str;
        
    return bin_map;

def _encodeData(data, binary_map):
    # Single character or no data
    if (len(binary_map) == 0):
        return None;

    res = bytearray();

    byte = 0;
    bit_count = 0;

    # Iterate over all the characters in the provided data set
    for i in range(0, len(data) + 1):
    
        # Append the data with the None key
        if (i == len(data)):
            bit_str = binary_map[None];
        else:
            bit_str = binary_map[data[i]];
    
        # Set the 1 bits for the current bit string 
        for bit in bit_str:
            if (bit == "1"):
                byte = _setBit(byte, bit_count);
            bit_count += 1;
            
            # Completed byte, add to the array
            if (bit_count == 8):
                res.extend(byte.to_bytes(1, _BITORDER));
                    
                byte = 0;
                bit_count = 0;
    
    # Non complete byte, add to the array
    if (bit_count != 0):
        res.extend(byte.to_bytes(1, _BITORDER));
        
    return res;
   
def _encodeFrequencyCharPairs(pairs):
    # Declare the frequency information
    freq_count = len(pairs) - 1;
    freq_byte_count = (pairs[freq_count].frequency.bit_length() + 7) // 8; # Max Frequency
    freq_buffer = bytearray();
    
    # Concatinate all the characters into a string and encode the frequencies
    char_str = "";
    for fc_pair in pairs:
        if (fc_pair.character is not None):
            char_str += fc_pair.character;
            freq_buffer.extend(fc_pair.frequency.to_bytes(freq_byte_count, _BITORDER));
    
    # Encode the remaining character and frequency data
    char_buffer = char_str.encode("utf-8");
    header_bytes = struct.pack(_modifyTypeFormat("IIB"), len(char_buffer), freq_count, freq_byte_count);
    
    bytes = _combineEncodedData(header_bytes, freq_buffer, char_buffer);
    
    # Write to file or return the byte array
    return bytes;
  
def _combineEncodedData(*byte_args):
    res = bytearray();
    
    for bytes in byte_args:
        res.extend(bytes);
        
    return res;


# Helper Methods
def _setBit(byte, bit):
    """
    Returns a new byte with the specified bit set to 1.
    
    @param byte: the byte that has its bit set to a 1
    @param bit: bit index, from 0 to 7
    
    @return: the modified byte value
    """

    if (bit < 0 or bit > 7):
        raise ValueError("'bit' must be between 0 and 7");

    return byte | (1 << (7 - bit));
    
def _getBit(byte, bit):
    """
    Returns whether or not the specified bit is set to 1.
    
    @param byte: the byte that has its bit indexed
    @param bit: bit index, from 0 to 7
    
    @return: True if the value of the specified bit is 1, otherwise false
    """

    if (bit < 0 or bit > 7):
        raise ValueError("'bit' must be between 0 and 7");
        
    return (byte & (1 << (7 - bit)) != 0);

def _formatFrequencyCharPairs(pairs, sort):
    """
    Inserts or appends the terminator pair to the list, and sorts the data.
    
    @param pairs: List of FrequencyCharPairs
    @param sort: True/False if the pairs list should be sorted. 
    
    @return: the modified list of FrequencyCharPairs
    """
        
    if (sort):
        pairs.append(_TERMINATOR);
        return sorted(pairs);
    else:
        pairs.insert(0, _TERMINATOR);
        return pairs;
  
def _modifyTypeFormat(type_str):
    """
    Appends the provided type string with the big or little endian symbol.
    
    @param type_str: type string used for packing or unpacking
    """
    symbol = ">" if (_BITORDER == 'big') else "<";
    
    return symbol + type_str;
  
def _convertBytesToInt(bytes):
    """
    Converts the specified byte array to an integer.
    
    @param bytes: byte array to be converted into an integer
    
    @return: the 4 byte integer representation of the supplied byte array
    """
    
    # Ensure the length is 4 bytes
    if (len(bytes) < 4):
        tmp = bytearray(bytes);
        bytes = bytearray([0] * (4 - len(bytes)));
        
        if (_BITORDER == 'big'):
            bytes.extend(tmp);
        else:
            tmp.extend(bytes);
            bytes = tmp;
        
    elif (len(bytes) > 4):
        raise ValueError("Cannot convert bytes to int, must be at most 4 bytes.");
       
    return struct.unpack(_modifyTypeFormat("I"), bytes)[0];


