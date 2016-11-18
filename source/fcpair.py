class FrequencyCharPair:
    def __init__(self, frequency, character):
        self.frequency = frequency;
        self.character = character;
        
        
    def __cmp__(self, other):
        """
        Compares two objects based on the stored frequency value.
        """
        if (isinstance(other, FrequencyCharPair)):
            return cmp(self.frequency, other.frequency);
        else:
            return cmp(self.frequency, other);
        
        
    def __lt__(self, other):
        """
        Returns true if the frequency is less than the value of the supplied 
        object, otherwise false.
        """
        if (isinstance(other, FrequencyCharPair)):
            return self.frequency < other.frequency;
        else:
            return self.frequency < other;

            
    def __gt__(self, other):
        """
        Returns true if the frequency is greater than the value of the supplied
        object, otherwise false.
        """
        if (isinstance(other, FrequencyCharPair)):
            return self.frequency > other.frequency;
        else:
            return self.frequency > other;