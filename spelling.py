from spellchecker import SpellChecker

# Bot that will take a local dictionary and language to train on word frequency to 
# mitigate the OCRs errors..

class Spell(SpellChecker):
        
    def __init__(self, words, local_dictionary):
        super().__init__(local_dictionary=local_dictionary)
        self.words = words
