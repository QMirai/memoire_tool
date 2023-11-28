import os
import json

"""
The script is designed to gather information from objective language CoNLL-U files and compile it into a JSON file. It 
structure includes 'id', 'directory‘ and 'files'.The JSON file serves as an input for the 'grew compile' command and 
form corpora. Grew, in turn, utilizes these corpora to match sentences based on requested patterns.
"""

package = "sud"
if package == "ud":
    path = r"D:\\cours\\linux\\ubuntu\\ubuntu-22.04.3\\share\\ud-treebanks-v2.12"
    directory = "/mnt/hgfs/share/ud-treebanks-v2.12/"
    objective_language = ("UD_English", "UD_French")
else:
    path = r"D:\\cours\\linux\\ubuntu\\ubuntu-22.04.3\\share\\sud-treebanks-v2.12"
    directory = "/mnt/hgfs/share/sud-treebanks-v2.12/"
    objective_language = ("SUD_English", "SUD_French")

corpora = []
for i in os.listdir(path):
    if i.startswith(objective_language):
        corpus = {"id": i, "directory": directory + i}
        files = []
        for j in os.listdir(path + "\\" + i):
            if os.path.basename(j).endswith('conllu'):
                print(j)
                files.append(j)
        corpus["files"] = files
        corpora.append(corpus)


eng_fre = {"corpora": corpora}

print(eng_fre)
output_path = r"D:\\cours\\linux\\ubuntu\\ubuntu-22.04.3\\share\\"
output_filename = 'eng_fre_' + package + '.json'
with open(os.path.join(output_path, output_filename), 'w', encoding='utf-8') as output:
    json.dump(eng_fre, output, indent='\t')
