import argparse
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def read_df(directory):
    return pd.read_csv(f"{directory}/df.csv")


def plot(df=None, directory=None):
    if df is None and directory is not None:
        df = read_df(directory)
        df = df["OVERALL, RunTime(ms)"] # TODO

    plt.figure(figsize=(10,5))
    ax = sns.barplot(data=df, ci="sd", capsize=0.05)
    ax.set_xlabel("observations", fontsize = 10)
    ax.set_ylabel("ms", fontsize = 10)
    ax.set_title(f"Standard deviation of overall runtime", fontsize = 15)
    ax.set_xticklabels(["runtime"], rotation=0)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    plot(directory=args.directory)
