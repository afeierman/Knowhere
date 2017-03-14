import glob
from re import search

filelist = glob.glob('C:/Users/William/Documents/DataScience/Projects/Knowhere/data/iphone/Emil*')
with open(fName, 'w+') as af:
    af.write('timestamp, sensor, data_name, data_display, data_raw\n')
    for fn in filelist:
        with open(fn, 'r+') as f:
            next(f)
            for line in f:
                if not search('Screen', line):
                    af.write(line)