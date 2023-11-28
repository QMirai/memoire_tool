#!/bin/bash

grew compile -i eng_fre_sud.json

for type in "raising_verb" "control_verb"
do
	input_dir="/mnt/hgfs/share/list_fre_${type}"
	echo $input_dir
	output_dir="/mnt/hgfs/share/output_${input_dir##*/}"
	mkdir -p "$output_dir"

	for file in "$input_dir"/*.req
	do
		echo "Processing $file"
		filename=$(basename -- "$file")
		filename="${filename%.*}"
		grew grep -request $file -i eng_fre_sud.json > "$output_dir"/output_sud_"$filename".json
	done
done

echo "Finished!"