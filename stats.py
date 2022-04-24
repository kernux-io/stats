import argparse
import os
import pandas as pd
import plot


def read_files(path):
    data = {}
    errors = {}
    filenames = os.listdir(path)
    for filename in filenames:
        if os.path.isfile(os.path.join(path, filename)) and ".txt" in filename:
            instance_id = filename.rsplit('_',1)[0]
            if instance_id not in errors.keys():
                errors[instance_id] = []

            with open(f"{path}/{filename}", 'r') as file:
                rows = file.readlines()[1:]
                if (len(rows) == 38):
                    if "instance" not in data.keys():
                        data["instance"] = [instance_id]
                    else:
                        data["instance"].append(instance_id)

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
                else:
                    errors[instance_id].append(filename)

    return pd.DataFrame.from_dict(data), errors


def write_df(df, directory, filename, header=False):
    df.to_csv(f"{directory}/{filename}", header=header)


def write_errors(errors, directory, filename):
    with open(f"{directory}/{filename}", 'w') as f:
        f.write(f',"instance_id","count","filenames"\n')
        for idx, instance_id in enumerate(errors.keys()):
            f.write(f'{idx},{instance_id},{len(errors[instance_id])},"{errors[instance_id]}"\n')


def calculate_stats(directory):
    df, errors = read_files(directory)
    mean = df.mean()
    median = df.median()
    std = df.std()

    write_df(df, directory, "df.csv", True)
    write_df(mean, directory, "mean.csv")
    write_df(median, directory, "median.csv")
    write_df(std, directory, "std.csv")
    write_errors(errors, directory, "errors.csv")

    return df


def main(directory):
    sub_dirs = [
        "unikernel_allocpool", 
        "unikernel_base",
        "unikernel_dce",
        "unikernel_dce-allocpool",
        "unikernel_falloc",
        "unikernel_fbuddyalloc",
    ]
    dfs = {}
    for sub_dir in sub_dirs:
        path = f"{directory}/{sub_dir}"
        if os.path.isdir(path):
            df = calculate_stats(path)
            dfs[sub_dir] = df

    plot.main(
        dfs=dfs,
        directory=directory,
        sub_dirs=sub_dirs,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
