import argparse
from distutils.command.clean import clean
import os
import re
from itertools import zip_longest as izip_longest

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)


def main(directory=None):
    tab='\t'
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and not filename.startswith("cleaned"):
                # Clean file for unnecessary headers
                with open(file_path, 'r') as fr:
                    lines = fr.readlines()
                    with open(file_path, 'w') as fw:
                        for line in lines:
                            if "PID" not in line:
                                fw.write(line)

                cleaned_log = []
                with open(file_path) as f:
                    instances = int(file_path.split('/')[1].split('_')[0].replace('i', ''))
                    
                    header = ['timestamp']
                    for iteration in range(0, instances):
                        header.append(f"i{iteration+1}_pid")
                        header.append(f"i{iteration+1}_cpu")
                        header.append(f"i{iteration+1}_mem")
                    cleaned_log.append(header)
                    
                    for lines in grouper(f, 1 + instances, ''):
                        assert len(lines) == 1 + instances
                        ts = lines[0].replace('\n', '')

                        row = [ts]
                        for line in lines[1:]:
                            if line.startswith(" "):
                                print(line)
                                values = re.sub(' +', ' ', line.replace('\n', '')).lstrip(' ').split(' ')
                                pid = values[0]
                                cpu = values[1]
                                mem = values[2]
                                row.append(pid)
                                row.append(cpu)
                                row.append(mem)
                        
                        if len(row) > 1:
                            cleaned_log.append(row)
                
                with open(f"{directory}/cleaned_{filename}", "w") as f:
                    for line in cleaned_log:
                        f.write(f"{tab.join(line)}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
