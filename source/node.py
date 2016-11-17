class HuffmanNode:
    def __init__(self, frequency, left = None, right = None, root = None):
        self.frequency = frequency;
        self.leftChild = left;
        self.rightChild = right;
        self.parent = root;
    
    def getChildren(self):
        return self.leftChild, self.rightChild;
        
    def __cmp__(self, other):
        if (isinstance(other, HuffmanNode)):
            return cmp(self.frequency, other.frequency);
        else:
            return cmp(self.frequency, other);
            
    def __lt__(self, other):
        if (isinstance(other, HuffmanNode)):
            return self.frequency < other.frequency;
        else:
            return self.frequency < other;
            
    def __gt__(self, other):
        if (isinstance(other, HuffmanNode)):
            return self.frequency > other.frequency;
        else:
            return self.frequency > other;