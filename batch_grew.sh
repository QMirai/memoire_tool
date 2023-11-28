#!/bin/bash

input_dir="/mnt/hgfs/share/list_fre_raising_verb"
output_dir="/mnt/hgfs/share/output_list_fre_raising_verb"

grew compile -i eng_fre_sud.json
mkdir -p "$output_dir"

for file in "$input_dir"/*.req
do
	echo "Processing $file"
	filename=$(basename -- "$file")
	filename="${filename%.*}"
	grew grep -request $file -i eng_fre_sud.json > "$output_dir"/output_sud_"$filename".json
done

echo "Finished!"
