#!/usr/bin/env python

import jellyfish
from multiprocessing import Pool
import codecs,sys
import unicodedata


frec_dict={}

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s))

def calculate_distance(word,originalword):
    min_distance=100.0
    for key in frec_dict.keys():
        distance=float(jellyfish.levenshtein_distance(word,key))
        if distance< min_distance:
            min_distance=distance
            similar_word = key
        if distance == min_distance:
            if frec_dict[key] < frec_dict[similar_word]:
                similar_word = key
    #frequency=int(reducefactor*frec_dict[similar_word])
    #print frequency
    if(len(word)>len(originalword)):
        reducefactor=min_distance/len(word)
    else:
        reducefactor=min_distance/len(originalword)
    frequency=int((1.0-reducefactor)*frec_dict[similar_word])
    #print originalword, word, similar_word
    if frequency <1:
        frequency=1
    #print word,similar_word,min_distance,reducefactor,frec_dict[similar_word]
    return [originalword,frequency]


def calculate_frequency(word,originalword):
    max_similarity=-1.0
    for key in frec_dict.keys():
        similarity=jellyfish.jaro_winkler_similarity(word,key)
        if similarity > max_similarity:
            max_similarity=similarity
            similar_word = key
        if similarity == max_similarity:
            if frec_dict[key] < frec_dict[similar_word]:
                similar_word = key
    frequency=int(max_similarity*float(frec_dict[similar_word]))
    #print(originalword,frequency, similar_word,frequency)
    #print(u" word="+originalword+u",f="+frequency)
    if frequency <1:
        frequency=1
    #print word,similar_word,min_distance,reducefactor,frec_dict[similar_word]
    #print(" word=",originalword,"f=",frequency)
    return [originalword,frequency]


def aggregate_data(result):
    new_word= u"word="+result[0]+u",f="+str(result[1])#+u",flags=,originalFreq="+unicode(result[1])#+",originalWord="+result[1]
    print(new_word)


if __name__ == '__main__':
  wordlist_frequency = codecs.open("main_el.combined",mode="r",encoding='utf-8')
  for line in wordlist_frequency:
    keys=line.split(',')
    word=''
    for item in keys:
        data=item.split('=')
        if data[0]==' word':
            #word=strip_accents(data[1]).lower()
            word=normalize(data[1]).lower()
        elif data[0]=='f':
            frec_dict[word]=int(data[1])
  full_dictionary=codecs.open("Greek.dic",mode="r",encoding='utf-8')
  pool=Pool(4)
  allowflag=False
  letter_to_process=sys.argv[1]
  #print letter_to_process
  for line in full_dictionary:
      #print type(line)
      originalword=line.strip()
      word2=strip_accents(originalword).lower()
      word=normalize(originalword).lower()
      #print type(word)
      #print word[0], len(word),word
      if word2[0] == letter_to_process:
          allowflag=True
      if word2[0]!=letter_to_process and allowflag:
          continue
      if allowflag: # and (word not in frec_dict.keys()):
        #print("Analyzing:",word)
        pool.apply_async(calculate_frequency,args = (word, originalword ),callback=aggregate_data)
  pool.close()
  pool.join()
