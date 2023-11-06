import csv
import pyconll
import os
import re

file_name_tsv = 'export-1000-UD_French-GSD.tsv'
file_name_conllu = 'export-1000-UD_French-GSD.conllu'
new_file = 'export' + re.findall(r'(-.*)\.', file_name_tsv)[0] + '_with_infinitive.csv'


def tsv_list(file):
    """
    Open the TSV (Tab-Separated Values) file, remove all the double quotation marks that can disrupt
    the file reading using csv.reader, and save the modified data to a temporary file called 'test'.
    Then, utilize csv.reader to return the data as a list in which each element represents a line of the CSV file
    in the form of a list.
    :param file: tsv.file
    :return: a list in which each element represents a line of the CSV file in the form of a list.
    """
    with open(file, 'r', encoding='utf-8') as tsv_file:
        data = tsv_file.read().replace('"', '')         # remove all the double quotation marks

    with open('test', 'w', encoding='utf-8') as clean_tsv:
        clean_tsv.write(data)                           # save to a temporary file

    with open('test', 'r', encoding='utf-8') as clean_tsv:
        data = csv.reader(clean_tsv, delimiter='\t')    # load the clean tsv file
        clean_list = [line for line in data]            # return a list of list
    os.remove('test')                                   # remove the temporary file
    return clean_list


data_tsv = tsv_list(file_name_tsv)[1:]                  # to skip the title line
data_conllu = pyconll.iter_from_file(file_name_conllu)  # load the conllu file and return an iter, whose element is a
                                                        # sentence object. Use loop for to iterate all the tokens.

# you can find all token attributes at the title line of conllu file
with open(new_file, 'w',  newline='', encoding='utf-8') as csvfile:
    new_data = csv.writer(csvfile, delimiter='\t')      # prepare for writing new data in csv format
    index = 0                                           # reduce the iterating element, no need to always start from 0
    for sentence in data_conllu:
        match = False                                   # if sent_id does not match, write '---------------' as a mark
        for i in range(index, len(data_tsv)):           # reduce the iterating element, no need to always start from 0
            if sentence.id == data_tsv[i][0]:           # tsv and conllu 's sent_id matching
                token_id = 0
                for token in sentence:                  # if matched, iterate all the tokens of sentence
                    token_id += 1                       # record index for getting the real lemma if 'gonna', "let's"
                    if token.form == data_tsv[i][2]:    # find the pivot word
                        new_line = data_tsv[i][:3]      # construct a new line containing : the sent_id, left context,
                                                        # pivot word, pivot word's infinitive
                        new_line.append(token.lemma if token.lemma else sentence[token_id].lemma)  # resolve 'gonna'...
                        new_line.append(data_tsv[i][-1])  # right context
                        # print(new_line)               # test : check every new line
                        new_data.writerow(new_line)     # write in new csv file
                        match = True
                        break                           # avoid duplicate write-in caused by other words identical to
                                                        # pivot word
        if not match:
            new_data.writerow(['-------------------'])
        index += 1                                      # reduce the iterating element, no need to always start from 0

# view the result
# for i in tsv_list(new_file):
#     print(i)
