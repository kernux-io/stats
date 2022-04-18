import argparse
import os
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def read_df(directory):
    path_df = f"{directory}/df.csv"
    if os.path.isfile(path_df):
        return pd.read_csv(path_df)


def plot(df, filename, figsize=(5,5), x="observation", y="value", hue="source", x_label="", y_label="", title="", labels=[]):
    plt.figure(figsize=figsize)
    ax = sns.barplot(x=x, y=y, data=df, ci="sd", capsize=0.05, hue=hue)
    ax.set_xlabel(x_label, fontsize = 10)
    ax.set_ylabel(y_label, fontsize = 10)
    ax.set_title(title, fontsize = 15)
    ax.set_xticklabels(labels, rotation=0)
    plt.show()
    fig = ax.get_figure()
    fig.savefig(filename)


def main(df_unikernel=None, df_docker=None, directory=None, dir_df1 = "unikernel", dir_df2 = "docker", errors_df1=[], errors_df2=[]):
    if directory is not None and df_unikernel is None:
        df_unikernel = read_df(f"{directory}/{dir_df1}")
    if directory is not None and df_docker is None:
        df_docker = read_df(f"{directory}/{dir_df2}")

    df_unikernel["source"] = dir_df1
    df_docker["source"] = dir_df2
    df_union = pd.concat([df_unikernel, df_docker], ignore_index=True)    
    
    df = df_union.copy()
    df["observation"] = "OVERALL, RunTime(ms)"
    df["value"] = df["OVERALL, RunTime(ms)"]
    df = df[["source", "observation", "value"]]

    for column in df_union.columns:
        if column not in ["OVERALL, RunTime(ms)", "Unnamed: 0", "source"]:
            df_observation = df_union.copy()
            df_observation["observation"] = column
            df_observation["value"] = df_observation[column]
            df_observation = df_observation[["source", "observation", "value"]]
            df = pd.concat([df, df_observation], ignore_index=True)

    print(df.to_string())

    print(f"\nUnikernel errors: {len(errors_df1)} ({errors_df1}) \
            \nDocker errors: {len(errors_df2)} ({errors_df2})")

    # Overall runtime (ms)
    df_plot = df.loc[df["observation"] == "OVERALL, RunTime(ms)"]
    plot(
        df_plot,
        f"{directory}/overall-runtime_{dir_df1}-{dir_df2}.svg",
        x_label="",
        y_label="ms",
        title="Overall runtime",
        labels=["total runtime"]
    )
    
    # Overall throughput (ops/sec)
    df_plot = df.loc[df["observation"] == "OVERALL, Throughput(ops/sec)"]
    plot(
        df_plot,
        f"{directory}/overall-throughput_{dir_df1}-{dir_df2}.svg",
        x_label="",
        y_label="sec",
        title="Overall throughput",
        labels=["operations"]
    )

    # Read (us)
    df_plot = df.loc[
        (df["observation"] == "READ, AverageLatency(us)") |
        (df["observation"] == "READ, MinLatency(us)") |
        (df["observation"] == "READ, MaxLatency(us)") |
        (df["observation"] == "READ, 95thPercentileLatency(us)") |
        (df["observation"] == "READ, 99thPercentileLatency(us)")
    ]
    plot(
        df_plot,
        f"{directory}/ops-read_{dir_df1}-{dir_df2}.svg",
        figsize=(12,5),
        x_label="",
        y_label="μs",
        title="Read operations",
        labels=[
            "average latency",
            "min latency",
            "max latency",
            "95th percentile latency",
            "99th percentile latency"
        ]
    )
    
    # Cleanup (us)
    df_plot = df.loc[
        (df["observation"] == "CLEANUP, AverageLatency(us)") |
        (df["observation"] == "CLEANUP, MinLatency(us)") |
        (df["observation"] == "CLEANUP, MaxLatency(us)") |
        (df["observation"] == "CLEANUP, 95thPercentileLatency(us)") |
        (df["observation"] == "CLEANUP, 99thPercentileLatency(us)")
    ]
    plot(
        df_plot,
        f"{directory}/ops-cleanup_{dir_df1}-{dir_df2}.svg",
        figsize=(12,5),
        x_label="",
        y_label="μs",
        title="Cleaup operations",
        labels=[
            "average latency",
            "min latency",
            "max latency",
            "95th percentile latency",
            "99th percentile latency"
        ]
    )

    # Insert (us)
    df_plot = df.loc[
        (df["observation"] == "INSERT, AverageLatency(us)") |
        (df["observation"] == "INSERT, MinLatency(us)") |
        (df["observation"] == "INSERT, MaxLatency(us)") |
        (df["observation"] == "INSERT, 95thPercentileLatency(us)") |
        (df["observation"] == "INSERT, 99thPercentileLatency(us)")
    ]
    plot(
        df_plot,
        f"{directory}/ops-insert_{dir_df1}-{dir_df2}.svg",
        figsize=(12,5),
        x_label="",
        y_label="μs",
        title="Insert operations",
        labels=[
            "average latency",
            "min latency",
            "max latency",
            "95th percentile latency",
            "99th percentile latency"
        ]
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
