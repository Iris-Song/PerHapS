import numpy as np
import pandas as pd
import os
import re
from collections import Counter
data_path = '../dataset/Metal_Content_of_Consumer_Products_Tested_by_the_NYC_Health_Department_20240403.csv'
df = pd.read_csv(data_path)
def missspell(df):
    def read_glove_vecs(glove_file):
        with open(glove_file,'r') as f:
            words=set()
            for line in f:
                line=line.strip().split()
                curr_word=line[0]
                words.add(curr_word)
            i=1
            words_to_index={}
            for w in sorted(words):
                words_to_index[w]=i
                i=i+1
        del words
        return words_to_index
    WORDS=read_glove_vecs('../dataset/glove.6B.50d.txt')
    def words(text):
        return re.findall(r'\w+', text.lower())
    def P(word):
        return -WORDS.get(word,0)
    def correction(word):
        return max(candidates(word), key=P)
    def candidates(word):
        c =  (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])
        return c
    def known(ws):
        return set(w for w in ws if w in WORDS)
    def edits1(word):
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)
    def edits2(word):
        return (e2 for e1 in edits1(word) for e2 in edits1(e1))
    def find_corrections(text):
        arr = text
        corrections_list = []
        for s in arr:
            s = s.lower()
            if s and correction(s) != s:
                corrections_list.append((s, correction(s)))
        return corrections_list
    corrections = []
    corrections_summary = []
    for index, line in df['MANUFACTURER'].items():
        row_corrections = find_corrections(words(line))
        corrections += row_corrections
        corrections_summary += [(original, corrected) for original, corrected in row_corrections if original != corrected]

        if row_corrections:
            df.at[index, 'MANUFACTURER'] = 'Misspell'
        else:
            df.at[index, 'MANUFACTURER'] = 'valid'
    corrections_df = pd.DataFrame(corrections_summary, columns=['Original', 'Corrected'])
    summary_df = corrections_df.groupby(['Corrected']).agg(Frequency=('Corrected', 'size')).reset_index()
    summary_df['Category'] = summary_df['Corrected'].apply(lambda x: 'Misspell' if x in corrections_df['Original'].values else 'Valid')
    summary_df = summary_df[['Corrected', 'Frequency', 'Category']]
    summary_df.columns = ['Value', 'Frequency', 'Category']
    return df,  summary_df 

df1, df2=missspell(df)
print(df1.head())
print(df2.head())