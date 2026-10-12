# Collect EuvsDisinfo
Use this repository to collect the EuvsDisinfo dataset described in our paper "EUvsDisinfo: a Dataset for Multilingual Detection of Pro-Kremlin Disinformation
in News Articles."

## Setup python environment:
    conda create -n euvsdisinfo python=3.11.5
    pip install -r requirements.txt

## To collect the data:
1. Download the supplementary data ```euvsdisinfo_base.csv``` and place it in this folder.
2. Run ```python3 collect.py```.
3. When finished, you should find a CSV file named ```euvsdisinfo.csv``` in this folder.

## Citing:
TBA