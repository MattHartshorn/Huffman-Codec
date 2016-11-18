class HuffmanNode:
    def __init__(self, frequency, left = None, right = None, root = None):
        self.frequency = frequency;
        self.leftChild = left;
        self.rightChild = right;
        self.parent = root;
    
    
    def getChildren(self):
        """
        Returns both the left and right children of the node.
        
        @return: a tuple of both left and right children
        """
        return self.leftChild, self.rightChild;
        
        
    def __cmp__(self, other):
        """
        Compares two objects based on the stored frequency value.
        """
    
        if (isinstance(other, HuffmanNode)):
            return cmp(self.frequency, other.frequency);
        else:
            return cmp(self.frequency, other);
    
    
    def __lt__(self, other):
        """
        Returns true if the frequency is less than the value of the supplied 
        object, otherwise false.
        """
        if (isinstance(other, HuffmanNode)):
            return self.frequency < other.frequency;
        else:
            return self.frequency < other;

            
    def __gt__(self, other):
        """
        Returns true if the frequency is greater than the value of the supplied
        object, otherwise false.
        """
        if (isinstance(other, HuffmanNode)):
            return self.frequency > other.frequency;
        else:
            return self.frequency > other;