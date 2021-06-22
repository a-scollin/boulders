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



span_counter = None    
j = i
k = i 
while not height and (j > 0 or k < len(spans) - 1):           
    
    if span_counter:
        # print("span")
        span_counter += 1 
        # print(span_counter)
        if span_counter > 6:
            height = spans[span_index].text
            breadth_index = span_index
            break
    
    if j > 0:
        j -= 1
    if k < len(spans) - 1:
        k += 1 
    for label in spans[j].labels:    
        if "CD" in label.value:
            # print("CD!")
            # print(spans[j].text)
            if (j != breadth_index and j != length_index and spans[j].text.isnumeric()):
                height = spans[j].text
                breadth_index = j
            
            # print(breadth_index)
            # print(j)
            # print(height)
            if span_counter == 0:
                if (j == breadth_index or j == length_index) and height is None:
                    # print("span on")
                    span_index = j
                    span_counter = 1 

                
    if not height:
        for label in spans[k].labels:
            if "CD" in label.value:
                if k != breadth_index and k != length_index and spans[k].text.isnumeric():
                    # print("K")
                    # print(span_counter)
                    # print(spans[k].text)

                    # print(i)
                    # print(j)
                    # print(k)
                    
                    height = spans[k].text 
                    breadth_index = k  

                if span_counter == 0:
                    if (j == breadth_index or j == length_index) and height is None:
                        # print("span on")
                        span_index = j
                        span_counter = 1 