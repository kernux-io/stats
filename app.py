import argparse
import json
import os
import pandas as pd
import plot


def read_files(path):
    data = {}
    filenames = os.listdir(path)
    for filename in filenames:
        if os.path.isfile(os.path.join(path, filename)) and ".txt" in filename:
            with open(f"{path}/{filename}", 'r') as file:
                rows = file.readlines()[1:]
                for row in rows:
                    row = row.replace('\n', '').split(', ')
                    operation = row[0].replace('[', '').replace(']', '')
                    event = row[1]
                    value = float(row[2])

                    key = f"{operation}, {event}"
                    if key not in data.keys():
                        data[key] = [value]
                    else:
                        data[key].append(value)
    return pd.DataFrame.from_dict(data)


def write_df(df, directory, filename, header=False):
    df.to_csv(f"{directory}/{filename}", header=header)


def main(args):
    directory = args.directory
    df = read_files(directory)
    print(f"\nDataFrame:\n{df}")
    
    mean = df.mean()
    print(f"\nMean (average):\n{mean}")
    
    median = df.median()
    print(f"\nMedian:\n{median}")

    std = df.std()
    print(f"\nStandard deviation:\n{std}")
    
    write_df(df, directory, "df.csv", True)
    write_df(mean, directory, "mean.csv")
    write_df(median, directory, "median.csv")
    write_df(std, directory, "std.csv")

    df = df["OVERALL, RunTime(ms)"] # TODO
    plot.plot(df) 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(args)
