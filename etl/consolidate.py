import os
import sys
import pandas as pd

data_set_path = "../data-uol-thesis-topics"
db_topics_filename = "db-topics.csv"
export_dir_set = set()

print('Starting the import and consolidation of the data set ({0}).'.format(data_set_path))
for dirname in os.listdir(data_set_path):
    export_dir_set.add(dirname)

export_dir_set = sorted(export_dir_set)

for export_dir in export_dir_set:
    # Exclude hidden/ system folders
    if export_dir.startswith('.'):
        continue

    print('Iterating over export folder {0}'.format(export_dir))
    db_topics_path = data_set_path + "/" + export_dir + "/" + db_topics_filename

    # Load data from db-topics.csv
    try:
        topic_df = pd.read_csv(db_topics_path, sep=";")
    except FileNotFoundError:
        print("The file {} does not exist.".format(db_topics_path))
    except Exception as e:
        print("An error occurred opening the file {}:".format(db_topics_path), e)
        sys.exit()
