# https://www.siggraph.org/education/materials/HyperGraph/video/mpeg/mpegfaq/huffman_tutorial.html

import sys;
import queue;
import pickle;
import io;
from operator import itemgetter;
from EncodedData import EncodedData;

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
    @staticmethod
    def encode(data):
        char_freq = HuffmanEncoder._getCharFrequencies(data);
        tree = HuffmanEncoder._createTree(char_freq);
        binary_map = HuffmanEncoder._getBinaryMap(tree);
        
        data_bytes = HuffmanEncoder._encodeDataToBytes(data, binary_map);
        
        encodedData = EncodedData(char_freq, data_bytes);
    
        bytes = pickle.dumps(encodedData, protocol=pickle.HIGHEST_PROTOCOL);
    
        return bytes;
        
    @staticmethod
    def decode(bytes):
        
        encodedData = pickle.load(io.BytesIO(bytes));
        print(encodedData.char_frequencies);
        return;
        
# Private Methods
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
        return sorted(res, key=itemgetter(0));
        
        
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
            
        
    @staticmethod
    def _getBinaryMap(tree_root):
        bin_map = {};
        
        # Empty tree
        if (tree_root == None):
            return bin_map;
        
        # Create the stack to house the nodes
        stack = [];
        stack.append((tree_root, "0"));
        
        while (stack):
            
            # Get the top item and discard the frequency summation
            sub_tree, bit_str = stack.pop();
            _, node = sub_tree;
            
            if (isinstance(node, tuple)):
                # Leaf Node, map the binary string to the character
                bin_map[node[1]] = bit_str;
            elif (isinstance(node, SubTree)):
                # Add the child nodes to the stack
                stack.append((node.getRightChild(), bit_str + "1"));
                stack.append((node.getLeftChild(), bit_str + "0"));
            else:
                # Single node in tree
                bin_map[node] = bit_str;
            
        return bin_map;
        
        
    @staticmethod
    def _readBytes(bytes):
        return;
        
    @staticmethod
    def _decodeBytes(tree, data_bytes):
        return;
        
        
    @staticmethod
    def _encodeDataToBytes(data, binary_map):
        bit_str = "";
    
        for char in data:
            bit_str += binary_map[char];
            
        return HuffmanEncoder._bitStringToBytes(bit_str);
        
        
    @staticmethod
    def _bitStringToBytes(bits):
        byte_length = 8;
    
    
        int_array = [int(bits[i:(i + byte_length)], 2) for i in range(0, len(bits), byte_length)];
        print(len(int_array));
        return bytearray(int_array);
 
 
data = "The quick brown fox jumps over the lazy dog";
#res = HuffmanEncoder._getBinaryMap(HuffmanEncoder._createTree(HuffmanEncoder._getCharSetFrequency(data)));
#print(len(res));
#print(BitArray(bin=HuffmanEncoder._encodeDataToBytes(data, res)));

#x = HuffmanEncoder._bitStringToBytes(HuffmanEncoder._encodeDataToBytes(data, res));

x = HuffmanEncoder.encode(data);
print(len(x));
#print(x);

#HuffmanEncoder.decode(x);
