class FrequencyCharPair:
    def __init__(self, frequency, character):
        self.frequency = frequency;
        self.character = character;
        
    def __cmp__(self, other):
        if (isinstance(other, FrequencyCharPair)):
            return cmp(self.frequency, other.frequency);
        else:
            return cmp(self.frequency, other);
            
    def __lt__(self, other):
        if (isinstance(other, FrequencyCharPair)):
            return self.frequency < other.frequency;
        else:
            return self.frequency < other;
            
    def __gt__(self, other):
        if (isinstance(other, FrequencyCharPair)):
            return self.frequency > other.frequency;
        else:
            return self.frequency > other;