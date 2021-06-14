from spellchecker import SpellChecker


class correction(SpellChecker):
        
    def __init__(self, words, local_dictionary):
        super().__init__(local_dictionary=local_dictionary)
        self.words = words


