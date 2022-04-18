import argparse
import os
import pandas as pd
import plot


def read_files(path):
    data = {}
    errors = []
    filenames = os.listdir(path)
    for filename in filenames:
        if os.path.isfile(os.path.join(path, filename)) and ".txt" in filename:
            with open(f"{path}/{filename}", 'r') as file:
                try:
                    rows = file.readlines()[1:]
                    if (len(rows) == 38):
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
                except:
                    errors.append(filename)
    print(data)

    return pd.DataFrame.from_dict(data), errors


def write_df(df, directory, filename, header=False):
    df.to_csv(f"{directory}/{filename}", header=header)


def calculate_stats(directory):
    df, errors = read_files(directory)
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

    return df, errors


def main(directory):
    dir_df1 = "unikernel"
    dir_df2 = "unikernel_dce-allocpool"

    df_unikernel = None
    df_docker = None
    errors_unikernel = None
    errors_docker = None

    path_unikernel = f"{directory}/{dir_df1}"
    if os.path.isdir(path_unikernel):
        df_unikernel, errors_unikernel = calculate_stats(path_unikernel)

    path_docker = f"{directory}/{dir_df2}"
    if os.path.isdir(path_docker):
        df_docker, errors_docker = calculate_stats(path_docker)

    plot.main(
        df_unikernel=df_unikernel,
        df_docker=df_docker,
        directory=directory,
        dir_df1=dir_df1,
        dir_df2=dir_df2,
        errors_df1=errors_unikernel,
        errors_df2=errors_docker
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
