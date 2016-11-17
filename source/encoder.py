import queue;
import struct;

from node import HuffmanNode;
from fcpair import FrequencyCharPair;


class HuffmanEncoder:
# Private Fields
    _BITORDER = 'little';
    _TERMINATOR = FrequencyCharPair(0, None);

    
# Public Methods

    @staticmethod
    def encode(data, ofile_name = None):
    
        # Declare and open the output file if provided
        ofile = None;
        if (ofile_name is not None):
            ofile = open(ofile_name, "wb+");
    
        # Compute the character/frequency listing
        fc_pairs = HuffmanEncoder._getFrequencyCharPairs(data);
        
        # Compute the tree and the associated binary map to help form the encoded data
        tree = HuffmanEncoder._createTree(fc_pairs);
        binary_map = HuffmanEncoder._getBinaryMap(tree);
        
        # Encode all the data
        header_buffer = HuffmanEncoder._encodeFrequencyCharPairs(fc_pairs);
        data_buffer = HuffmanEncoder._encodeData(data, binary_map);
        
        if (ofile is not None):
            # Write the data to the output file
            ofile.write(header_buffer);
            ofile.write(data_buffer);
            ofile.close(); 
        else:  
            # Combine and return the byte data
            return HuffmanEncoder._combineEncodedData(header_buffer, data_buffer);
        
    @staticmethod
    def decode(bytes, ofile_name = None):
    
        # Declare and open the output file if provided
        ofile = None;
        if (ofile_name is not None):
            ofile = open(ofile_name, "w+");
    
        # Unpack the header data
        char_byte_count, freq_count, freq_byte_count = struct.unpack_from(HuffmanEncoder._modifyTypeFormat("IIB"), bytes, 0);
        offset = 9;
        
        # Get and decode the frequencies
        freq_buffer = bytes[offset:offset + (freq_count * freq_byte_count)];
        offset += (freq_count * freq_byte_count);
        frequencies = HuffmanEncoder._decodeFrequencies(freq_buffer, freq_byte_count);
        
        # Get and decode the character array
        char_buffer = bytes[offset:offset + char_byte_count];
        offset += char_byte_count;
        fc_pairs = HuffmanEncoder._decodeFrequencyCharPairs(char_buffer, frequencies);
       
        # Create the huffman tree and decode the data
        tree = HuffmanEncoder._createTree(fc_pairs);
        decoded_data = HuffmanEncoder._decodeDataBytes(tree, bytes[offset:]);
        
        # Write or return the data
        if (ofile is not None):
            ofile.write(decoded_data);
            ofile.close();
        else:
            return decoded_data;
        
        
    @staticmethod
    def encodeFile(ifile_name, ofile_name = None):
    
        ifile = open(ifile_name, "r");
        data = ifile.read();
        ifile.close();
    
        bytes = HuffmanEncoder.encode(data, ofile_name);
        
        return bytes;
        
    @staticmethod
    def decodeFile(ifile_name, ofile_name = None):
    
        ifile = open(ifile_name, "rb");
        bytes = ifile.read();
        ifile.close();
    
        data = HuffmanEncoder.decode(bytes, ofile_name);
        
        return data;
    
        
        
# Private Methods
    @staticmethod
    def _createTree(frequency_char_pairs):
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
    @staticmethod
    def _decodeFrequencyCharPairs(char_buffer, frequencies):  
        chars = char_buffer.decode();
    
        # Determine if the lengths match
        if (len(chars) != len(frequencies)):
            raise ValueError("The length of the character array and frequencies dont match");
    
        # Combine the arrays into a tuple array
        res = [];
        for i in range(0, len(chars)):
            res.append(FrequencyCharPair(frequencies[i], chars[i]));
        
        return HuffmanEncoder._formatFrequencyCharPairs(res, False);
    
    @staticmethod                   
    def _decodeFrequencies(freq_buffer, freq_byte_count):
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
            res.append(HuffmanEncoder._convertBytesToInt(bytes));
            
        return res;
    
    @staticmethod
    def _decodeDataBytes(tree_root, data_bytes):
    
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
                    bit_val = HuffmanEncoder._getBit(byte, bit);
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
       

    # Encoding
    @staticmethod
    def _getFrequencyCharPairs(data):
        
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
        return HuffmanEncoder._formatFrequencyCharPairs(res, True);
    
    @staticmethod
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
    
    @staticmethod
    def _encodeData(data, binary_map, ofile = None):
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
                    res.extend(byte.to_bytes(1, HuffmanEncoder._BITORDER));
                        
                    byte = 0;
                    bit_count = 0;
        
        # Non complete byte, add to the array
        if (bit_count != 0):
            res.extend(byte.to_bytes(1, HuffmanEncoder._BITORDER));
            
        if (ofile is not None):
            ofile.write(res);
        else:
            return res;
    
    @staticmethod    
    def _encodeFrequencyCharPairs(pairs, ofile = None):
        # Declare the frequency information
        freq_count = len(pairs) - 1;
        freq_byte_count = (pairs[freq_count].frequency.bit_length() + 7) // 8; # Max Frequency
        freq_buffer = bytearray();
        
        # Concatinate all the characters into a string and encode the frequencies
        char_str = "";
        for fc_pair in pairs:
            if (fc_pair.character is not None):
                char_str += fc_pair.character;
                freq_buffer.extend(fc_pair.frequency.to_bytes(freq_byte_count, HuffmanEncoder._BITORDER));
        
        # Encode the remaining character and frequency data
        char_buffer = char_str.encode();
        header_bytes = struct.pack(HuffmanEncoder._modifyTypeFormat("IIB"), len(char_buffer), freq_count, freq_byte_count);
        
        bytes = HuffmanEncoder._combineEncodedData(header_bytes, freq_buffer, char_buffer);
        
        # Write to file or return the byte array
        if (ofile is not None):
            ofile.write(bytes);
        else:
            return bytes;
      
    @staticmethod
    def _combineEncodedData(*byte_args):
        res = bytearray();
        
        for bytes in byte_args:
            res.extend(bytes);
            
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
    def _formatFrequencyCharPairs(pairs, sort):        
        if (sort):
            pairs.append(HuffmanEncoder._TERMINATOR);
            return sorted(pairs);
        else:
            pairs.insert(0, HuffmanEncoder._TERMINATOR);
            return pairs;
      
    @staticmethod
    def _modifyTypeFormat(type_str):
        
        symbol = ">" if (HuffmanEncoder._BITORDER == 'big') else "<";
        
        return symbol + type_str;
      
    @staticmethod
    def _convertBytesToInt(bytes):
        
        # Ensure the length is 4 bytes
        if (len(bytes) < 4):
            tmp = bytearray(bytes);
            bytes = bytearray([0] * (4 - len(bytes)));
            
            if (HuffmanEncoder._BITORDER == 'big'):
                bytes.extend(tmp);
            else:
                tmp.extend(bytes);
                bytes = tmp;
            
        elif (len(bytes) > 4):
            raise ValueError("Cannot convert bytes to int, must be at most 4 bytes.");
           
        return struct.unpack(HuffmanEncoder._modifyTypeFormat("I"), bytes)[0];
 

