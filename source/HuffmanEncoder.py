# https://www.siggraph.org/education/materials/HyperGraph/video/mpeg/mpegfaq/huffman_tutorial.html

import sys;
import queue;
import io;
from struct import unpack;
from operator import itemgetter;

class SubTree:
    def __init__(self, left = None, right = None, root = None):
        self._left = left;
        self._right = right;
        self._root = root;
    
    def getParent(self):
        return self._root;
    
    def getChildren(self):
        return self._left, self._right;
        
    def getLeftChild(self):
        return self._left;
        
    def getRightChild(self):
        return self._right;
        
    def __lt__(self, other):
        return False;
    
    def __gt__(self, other):
        return True;
        

class HuffmanEncoder:
    _BITORDER = 'big';

# Public Methods

    @staticmethod
    def encode(data):
    
        # Compute the character/frequency listing
        char_freq = HuffmanEncoder._getCharFrequencies(data);
        
        # Compute the tree and the associated binary map to help form the encoded data
        tree = HuffmanEncoder._createTree(char_freq);
        binary_map = HuffmanEncoder._getBinaryMap(tree);
        
        # Encode the input data
        data_bytes = HuffmanEncoder._encodeDataToBytes(data, binary_map);
    
        # Encode the Characters and Frequencies
        bytes = HuffmanEncoder._encodeCharFrequencies(char_freq);
        
        # Append the main data to then of the character/frequency bytes
        bytes.extend(data_bytes);
        
        return bytes;
        
    @staticmethod
    def decode(bytes):
        
        
        
        return;
        
        
        
# Private Methods
    @staticmethod
    def _createTree(char_frequencies):
        heap = queue.PriorityQueue();
        
        # Place all the frequencies and characters into the heap
        for value in char_frequencies:
            heap.put(value);
           
        while (heap.qsize() > 1):
            # Get the left and right items
            left = heap.get();
            right = heap.get();
            
            # Compute the sum of the frequencies and create the Sub-Tree to store in the queue
            sum_freq = left[0] + right[0];
            sub_tree = SubTree(left, right);

            # Insert the new sub-tree into the heap
            heap.put((sum_freq, sub_tree));
            
        # Return the root element which forms the tree
        return heap.get();
        
        
    # Decoding 
    @staticmethod
    def _partitionBytes(bytes):
        return;
    
    @staticmethod
    def _decodeCharFrequencies(char_buffer, frequencies):  
        chars = char_buffer.decode();
    
        # Determine if the lengths match
        if (len(chars) != len(frequencies)):
            raise ValueError("The length of the character array and frequencies dont match");
    
        # Combine the arrays into a tuple array
        res = [];
        for i in range(0, len(chars)):
            res.append((frequencies[i], chars[i]));
        
        return HuffmanEncoder._formatCharFrequencies(res, False);
    
    @staticmethod                   
    def _decodeFrequencies(freq_buffer, freq_byte_count):
        # Invalid input
        if (freq_byte_count <= 0 or freq_byte_count > 4):
            raise ValueError("Invalid frequency byte count, must be greater than zero and less than or equal to 4");
        elif (len(freq_buffer) % freq_byte_count != 0):
            raise ValueError("Invalid length for the frequency buffer, must be a multiple of " + freq_byte_count);
            
        res = [];
        
        # Determine the decoding endianness
        type = ">I" if (HuffmanEncoder._BITORDER == 'big') else "<I";
        
        # Loop over all the frequencies
        for i in range(0, len(freq_buffer), freq_byte_count):
            curr_freq = None;
            
            # Fill the byte array with any missing bytes
            if (4 - freq_byte_count > 0):
                curr_freq = bytearray([0] * (4 - freq_byte_count));
        
            # Retrieve the set of bytes
            if (curr_freq == None):
                curr_freq = freq_buffer[i:i + freq_byte_count];
            else:
                curr_freq.extend(freq_buffer[i:i + freq_byte_count]);
            
            # Unpack the frequency value
            res.append(unpack(type, curr_freq)[0]);
            
        return res;
    
    @staticmethod
    def _decodeDataBytes(tree, data_bytes):
    
        # Check for empty tree
        if (tree == None and data_bytes != None):
            raise ValueError("tree is empty");
        
        # Check if the data bytes value is valid
        if (data_bytes == None):
            raise ValueError("data_bytes cannot be None");
        elif (len(data_bytes) == 0):
            return "";
    
    
        # Initialize the result value and the sub_tree container to the root node
        res = "";
        sub_tree = tree[1];
        
        for byte in data_bytes:
            bit = 0;
        
            while (True):
                if (isinstance(sub_tree, SubTree)):
                    # Non-leaf, traverse left or right and increment bit 
                    bit_val = HuffmanEncoder._getBit(byte, bit);
                    bit += 1;
                    
                    if (bit_val):
                        sub_tree = sub_tree.getRightChild()[1];
                    else:
                        sub_tree = sub_tree.getLeftChild()[1];
                elif (sub_tree == None):
                    return res;
                else:
                    # Add the leaf character value, and reset the tree to the head
                    res += sub_tree;
                    sub_tree = tree[1];
            
            
                # Fetch next byte
                if (bit == 8):
                    break;
        
        return res;
        
        
    # Encoding
    @staticmethod
    def _getCharFrequencies(data):
        
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
            res.append((frequency, char));
        
        #return res;
        return HuffmanEncoder._formatCharFrequencies(res, True);
    
    @staticmethod
    def _getBinaryMap(tree_root):
        bin_map = {};
        
        # Empty tree
        if (tree_root == None):
            return bin_map;
        
        # Create the stack to house the nodes
        stack = [];
        stack.append((tree_root, ""));
        
        while (stack):
            
            # Get the top item and discard the frequency summation
            sub_tree, bit_str = stack.pop();
            _, node = sub_tree;
            
            if (isinstance(node, SubTree)):
                # Add the child nodes to the stack
                stack.append((node.getRightChild(), bit_str + "1"));
                stack.append((node.getLeftChild(), bit_str + "0"));
            else:
                # Leaf Node, map the binary string to the character
                bin_map[node] = bit_str;
            
        return bin_map;
    
    @staticmethod
    def _encodeDataToBytes(data, binary_map):
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
                    byte = HuffmanEncoder._setBit(byte, bit_count);
                bit_count += 1;
                
                # Completed byte, add to the array
                if (bit_count == 8):
                    res.append(byte);
                    byte = 0;
                    bit_count = 0;
        
        # Non complete byte, add to the array
        if (bit_count != 0):
            res.append(byte);
            
            
        return res;
    
    @staticmethod    
    def _encodeCharFrequencies(char_frequencies):
        # Declare the frequency information
        freq_count = len(char_frequencies);
        freq_byte_count = (char_frequencies[freq_count - 1][0].bit_length() + 7) // 8;
        freq_buffer = bytearray();
        
        # Concatinate all the characters into a string and encode the frequencies
        char_str = "";
        f = "";
        for value in char_frequencies:
            if (value[1] != None):
                char_str += value[1];
                freq_buffer.extend(value[0].to_bytes(freq_byte_count, HuffmanEncoder._BITORDER));
                f += str(value[0]) + ",";
        
        
        # Encode the remaining character and frequency data
        char_buffer = char_str.encode();
        char_byte_count = len(char_buffer).to_bytes(4, HuffmanEncoder._BITORDER);
        freq_byte_count = freq_byte_count.to_bytes(1, HuffmanEncoder._BITORDER);
        freq_count = freq_count.to_bytes(4, HuffmanEncoder._BITORDER);
        
        
        # Add all the binary arrays to the resulting array
        res = bytearray();
        res.extend(char_byte_count);
        res.extend(char_buffer);
        res.extend(freq_count);
        res.extend(freq_byte_count);
        res.extend(freq_buffer);
        
        return res;
        
    
    # Helper Methods
    @staticmethod
    def _setBit(byte, bit):
        if (bit < 0 or bit > 7):
            raise ValueError("'bit' must be between 0 and 7");
 
        return byte | (1 << (7 - bit));
        
    @staticmethod
    def _getBit(byte, bit):
        if (bit < 0 or bit > 7):
            raise ValueError("'bit' must be between 0 and 7");
            
        return (byte & (1 << (7 - bit)) != 0);
 
    @staticmethod
    def _formatCharFrequencies(char_frequencies, sort):
        
        terminator = (0, None);
        
        if (sort):
            char_frequencies.append(terminator);
            return sorted(char_frequencies, key=itemgetter(0));
        else:
            char_frequencies.insert(0, terminator);
            return char_frequencies;
        
 
# input is 359 bytes
data = "The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.";


x = HuffmanEncoder.encode(data);

print(len(x)); # output byte count
print(x); # binary representation






















