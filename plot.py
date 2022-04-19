import argparse
import os
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def read_df(directory, filename):
    path_df = f"{directory}/{filename}"
    if os.path.isfile(path_df) and os.stat(path_df).st_size > 0:
        return pd.read_csv(path_df)


def plot(df, filename, figsize=(5,5), x="observation", y="value", hue="source", x_label="", y_label="", title="", labels=[], rotation=0):
    plt.figure(figsize=figsize)
    ax = sns.barplot(x=x, y=y, data=df, ci="sd", capsize=0.05, hue=hue)
    ax.set_xlabel(x_label, fontsize = 8)
    ax.set_ylabel(y_label, fontsize = 8)
    ax.set_title(title, fontsize = 15)
    if labels != []:
        ax.set_xticklabels(labels, rotation=rotation)
    plt.show()
    fig = ax.get_figure()
    fig.savefig(filename)


def main(df_unikernel=None, df_docker=None, directory=None, dir_df1 = "unikernel", dir_df2 = "docker", errors_df1=None, errors_df2=None):
    if directory is not None:
        if df_unikernel is None:
            df_unikernel = read_df(f"{directory}/{dir_df1}", "df.csv")
        if df_docker is None:
            df_docker = read_df(f"{directory}/{dir_df2}", "df.csv")
        if errors_df1 is None:
            errors_df1 = read_df(f"{directory}/{dir_df1}", "errors.csv")
        if errors_df2 is None:
            errors_df2 = read_df(f"{directory}/{dir_df2}", "errors.csv")

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

    print(f"\nUnikernel errors: {(errors_df1['count'] > 0).value_counts()}\n{errors_df1.loc[errors_df1['count'] > 0]}")
    print(f"\nDocker errors: {(errors_df2['count'] > 0).value_counts()}\n{errors_df2.loc[errors_df2['count'] > 0]}")
    print(errors_df1.index)

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

    # Errors in 1st dataframe
    if errors_df1['instance_id'].count() > 0:
        plot(
            errors_df1,
            f"{directory}/errors_{dir_df1}.svg",
            figsize=(12,5),
            x="instance_id",
            y="count",
            hue=None,
            x_label="errors",
            y_label="count",
            title="Number of errors",
        )

    # Errors in 2nd dataframe
    if errors_df2['instance_id'].count() > 0:
        plot(
            errors_df2,
            f"{directory}/errors_{dir_df2}.svg",
            figsize=(12,5),
            x="instance_id",
            y="count",
            hue=None,
            x_label="errors",
            y_label="count",
            title="Number of errors",
        )

    plot(
        df_unikernel,
        f"{directory}/instances_overall-runtime_{dir_df1}.svg",
        x="instance",
        y="OVERALL, RunTime(ms)",
        x_label="instances",
        y_label="ms",
        title="Overall runtime",
    )

    plot(
        df_docker,
        f"{directory}/instances_overall-runtime_{dir_df2}.svg",
        x="instance",
        y="OVERALL, RunTime(ms)",
        x_label="instances",
        y_label="ms",
        title="Overall runtime",
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
