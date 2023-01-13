import os
from pathlib import Path
import pandas as pd

path = "../uol_thesis_topics"

for filename in os.listdir(path):
    print(filename)

print('Starting the import and consolidation of the data set.')

print('Iterating over day folder {0}'.format())
