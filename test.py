from flair.data import Sentence
from flair.models import MultiTagger
from flair.models import SequenceTagger
from flair.tokenization import SegtokSentenceSplitter

tagger = MultiTagger.load(['pos','ner'])

flair_sentence = Sentence("The dog went to the park and ate an apple.")

tagger.predict(flair_sentence)

spans = flair_sentence.get_spans('pos')

print(type(spans))
print(spans[2]["labels"])