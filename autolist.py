import csv
import pyconll
import re
import json
import os


def output_filename(path, new_extension='.csv'):
    path_without_ext, extension = os.path.splitext(path)
    output_folder_name = re.search(r"\\\\(output.+verb)", path_without_ext).group(1)
    return output_folder_name, os.path.basename(path_without_ext) + new_extension


class AutoList:
    def __init__(self, input_tsv, input_conllu):
        self.input_tsv = input_tsv
        self.input_conllu = input_conllu
        self.new_file = 'export' + re.findall(r'(-.*)\.', input_tsv)[0] + '_with_infinitive.csv'
        self.data_tsv = self.__tsv_list(self.input_tsv)
        self.data_conllu = pyconll.iter_from_file(self.input_conllu)
        # load the conllu file and return an iter, whose element is a
        # sentence object. Use loop for to iterate all the tokens.

    @staticmethod
    def __tsv_list(file):
        """
        Open the TSV (Tab-Separated Values) file, utilize `csv.reader` to return the data as a list in which each
        element represents a line of the CSV file in the form of a list.
        :param file: tsv.file
        :return: a list in which each element represents a line of the CSV file in the form of a list.
        """

        with open(file, 'r', encoding='utf-8') as clean_tsv:
            data = csv.reader(clean_tsv, delimiter='\t', quotechar=None)  # load the clean tsv file
            clean_list = [line for line in data]  # return a list of list
        return clean_list[1:]  # to skip the title line

    # you can find all token attributes at the title line of conllu file
    def insert_infinitive(self):
        with open(self.new_file, 'w', newline='', encoding='utf-8') as csvfile:
            new_data = csv.writer(csvfile, delimiter='\t')  # prepare for writing new data in csv format
            index = 0  # reduce iterating element, not always start from 0
            for sentence in self.data_conllu:
                match = False
                for i in range(index, len(self.data_tsv)):  # start from where last loop stopped
                    if sentence.id == self.data_tsv[i][0]:  # tsv and conllu 's sent_id matching
                        token_id = 0
                        for token in sentence:  # if matched, iterate all the tokens of sentence
                            token_id += 1  # record index for getting the real lemma if 'gonna', "let's"
                            if token.form == self.data_tsv[i][2]:  # find the pivot word
                                new_line = self.data_tsv[i][:3]  # construct a new line containing : the sent_id
                                # , left context, pivot word, pivot word's infinitive
                                new_line.append(
                                    token.lemma if token.lemma else sentence[token_id].lemma)  # resolve 'gonna'...
                                new_line.append(self.data_tsv[i][-1])  # right context
                                # print(new_line)               # test : check every new line
                                new_data.writerow(new_line)  # write in new csv file
                                match = True
                                break  # avoid duplicate write-in caused by other words identical to
                                # pivot word
                if not match:
                    raise Exception('{} not found in {}'.format(sentence.id, self.input_conllu))
                index += 1  # reduce the iterating element, no need to always start from 0


class GrewAutoList:
    def __init__(self, input_json, input_conllu_json):
        self.input_json = input_json
        self.input_conllu_json = input_conllu_json
        self.output_folder_name, self.output_filename = output_filename(self.input_json)
        with open(self.input_conllu_json, 'r', encoding='utf-8') as read_content:
            self.uds = json.load(read_content)['corpora']
        with open(self.input_json, 'r', encoding='utf-8') as read_content:
            self.data_list = json.load(read_content)

    def __preparation_conllus(self, ud_json) -> list:
        """
        Use corpora file to prepare 1-3 conllu files in an ud.
        :param ud_json: UDs in grew output file, like "UD_French-Sequoia"
        :return: combination of all conllu files in a UD
        """
        conllus = []
        for index in range(len(self.uds) - 1, -1, -1):  # order in conllu_list opposed to order in sentences_list
            if self.uds[index]["id"] == ud_json:
                directory = re.search(r"/share/(.*)", self.uds[index]["directory"])
                path_conllu = r"D:\\cours\\linux\\ubuntu\\ubuntu-22.04.3\\share\\" + directory.group(1)
                for conllu in self.uds[index]["files"]:
                    conllus += pyconll.load_from_file(os.path.join(path_conllu, conllu))
                conllus = sorted(conllus, key=lambda x: x.id)  # necessary, not always in order in test conllu part.
        return conllus

    def __preparation_sent(self) -> iter:
        """
        According to grew output file, make the ordered sentences and conllus an iter. ud is for locating not found
        files in raise.
        :return:
        """
        for ud, selected_sents in self.data_list.items():
            if len(selected_sents):
                ordered_sents = sorted(selected_sents, key=lambda x: x['sent_id'])
                conllus = self.__preparation_conllus(ud)
                yield ordered_sents, conllus, ud

    @staticmethod
    def __accurate_split(sent_json, objective_token):
        new_sent = ''
        split_text = ''
        # contraction_id = []
        for token in sent_json:
            # if "-" in token.id:
            #     if token.form in {'gonna', 'wanna', "let's", "don't", '__'}:
            #         contraction_id = [token.id]
            #     else:
            #         contraction_id = token.id.split("-")
            # if token.id not in contraction_id:
            seq = token.form if token.form else ''
            if token.id == objective_token:
                seq = "$" + seq + "$"
                split_text = seq
            new_sent += seq + ('' if "SpaceAfter=No" in token.misc else ' ')
        # print(split_text)
        # print(new_sent)
        return new_sent.split(split_text)

    @staticmethod
    def get_gp(conllu_sent, token_id):
        """
        It will iterate all the tokens of a sentence once.
        :param conllu_sent: target sentence.
        :param token_id: target verb's token id.
        :return: GP that the sentence reflects, e.g. `N_V_N`.
        """
        ignore_deprel = {'mod', 'punct', 'dislocated', 'cc', 'discourse', 'vocative', 'udep', 'conj', 'conj:coord',
                         'conj:dicto', 'conj:appos', 'parataxis', 'parataxis:insert'}
        # concerned_deprel = {'subj@expl', 'PRON', 'NOUN', 'PROPN', 'VERB', 'AUX', 'SCONJ', 'ADP'}
        gp_elements = []
        token_prep_id = ''  # record the target verb governing preposition's token id, e.g.`à` in `commencer à`.
        token_conj_id = ''
        ids = [token_id, token_prep_id, token_conj_id]
        moods = ['Cnd', 'Sub', 'Inf', 'Part', 'Ind']

        def get_mood(_token):
            """Return V or subordinate V + mood suffix or verb form suffix, e.g. Vcnd, Vsub"""
            for mood in moods:
                if mood in _token.feats.get('Mood', '') or mood in _token.feats.get('VerbForm', ''):
                    return f'V{mood.lower()}'
            else:
                return 'V'

        for token in conllu_sent:
            if token.head in ids and\
                    token.deprel not in ignore_deprel and\
                    not (token.deprel == 'subj@expl' and '-' in token.form):  # exclude -t-il
                if token.deprel == 'subj@expl':  # il expletive
                    gp_elements.append('Exp')
                elif token.upos in {'PRON', 'NOUN', 'PROPN', 'NUM'}:
                    gp_elements.append('N')
                elif token.upos in {'VERB', 'AUX'}:
                    gp_elements.append(get_mood(token))
                elif token.upos == 'SCONJ':
                    ids[2] = token.id
                    gp_elements.append(token.lemma)
                elif token.upos == 'ADP':
                    ids[1] = token.id
                    gp_elements.append(token.lemma)
                else:
                    gp_elements.append(token.upos)
            elif token.id == token_id:
                gp_elements.append("V")
        gp = '_'.join(gp_elements)
        return gp

    # @staticmethod
    # def __gp(conllu_sent, token_id):
    #     ignore_deprel = {'mod', 'punct', 'dislocated', 'cc', 'discourse', 'vocative', 'udep', 'conj', 'conj:coord',
    #                      'conj:dicto', 'conj:appos', 'parataxis'}
    #     deps = [token for token in conllu_sent if token.head == token_id and token.deprel not in ignore_deprel]
    def insert_infinitive(self):
        os.makedirs(f"output/{self.output_folder_name}", exist_ok=True)
        with open(os.path.join("output", self.output_folder_name, self.output_filename), 'w', newline='',
                  encoding='utf-8') as csvfile:
            new_data = csv.writer(csvfile, delimiter='\t')
            for sentences_ordered, conllus, ud in self.__preparation_sent():
                index = 0
                for sent_json in sentences_ordered:
                    found_match = False
                    i = index
                    while i < len(conllus):
                        if sent_json['sent_id'] == conllus[i].id:
                            line = []
                            token_id = sent_json['matching']['nodes']['G']
                            token_goal = conllus[i][token_id]
                            # if conllus[i][token_id].head != "0":
                            #     if conllus[i][conllus[i][token_id].head].upos in {'AUX', 'VERB'}:
                            #         token_goal_aux = conllus[i][token_id].head
                            #     else:
                            #         token_goal_aux = None
                            # else:
                            #     token_goal_aux = None
                            contexts = self.__accurate_split(conllus[i], token_goal.id) \
                                if conllus[i].text.count(token_goal.form) != 1\
                                else conllus[i].text.split(token_goal.form)
                            line.extend((conllus[i].id,
                                         token_goal.lemma,
                                         self.get_gp(conllus[i], token_id),
                                         contexts[0],
                                         token_goal.form,
                                         contexts[1]))
                            new_data.writerow(line)
                            print(line)
                            found_match = True
                            break  # if matched, break, don't `i += 1`. Keep this i in case of same sent_ids in json
                        i += 1  # if not matched, go for corpus's next sentence
                    if found_match:
                        index = i  # if matched, keep or upgrade the index
                    else:
                        raise Exception('{} not found in {}'.format(sent_json['sent_id'], ud))
