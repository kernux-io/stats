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


def main(dfs=None, directory=None, sub_dirs=None, error_dfs=None):
    if directory is not None:
        sub_dirs = [
            "unikernel_allocpool", 
            "unikernel_base",
            "unikernel_dce",
            "unikernel_dce-allocpool",
            "unikernel_falloc",
            "unikernel_fbuddyalloc",
        ]

        dfs = {}
        error_dfs = {}
        for sub_dir in sub_dirs:
            path = f"{directory}/{sub_dir}"
            df = read_df(path, "df.csv")
            error_df = read_df(path, "errors.csv")
            if df is not None:
                df["source"] = sub_dir
                dfs[sub_dir] = df
            if error_df is not None:
                error_dfs[sub_dir] = error_df

    dfs_list = []
    for key in dfs.keys():
        dfs_list.append(dfs[key])

    df_union = pd.concat(dfs_list, ignore_index=True)    
    
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

    #print(f"\nUnikernel errors: {(errors_df1['count'] > 0).value_counts()}\n{errors_df1.loc[errors_df1['count'] > 0]}")
    #print(f"\nDocker errors: {(errors_df2['count'] > 0).value_counts()}\n{errors_df2.loc[errors_df2['count'] > 0]}")
    #print(errors_df1.index)

    # Overall runtime (ms)
    df_plot = df.loc[df["observation"] == "OVERALL, RunTime(ms)"]
    plot(
        df_plot,
        #f"{directory}/overall-runtime_{dir_df1}-{dir_df2}.svg",
        f"{directory}/overall-runtime.svg",
        x_label="",
        y_label="ms",
        title="Overall runtime",
        labels=["total runtime"]
    )
    
    # Overall throughput (ops/sec)
    df_plot = df.loc[df["observation"] == "OVERALL, Throughput(ops/sec)"]
    plot(
        df_plot,
        #f"{directory}/overall-throughput_{dir_df1}-{dir_df2}.svg",
        f"{directory}/overall-throughput.svg",
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
        #f"{directory}/ops-read_{dir_df1}-{dir_df2}.svg",
        f"{directory}/ops-read.svg",
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
        #f"{directory}/ops-cleanup_{dir_df1}-{dir_df2}.svg",
        f"{directory}/ops-cleanup.svg",
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
        #f"{directory}/ops-insert_{dir_df1}-{dir_df2}.svg",
        f"{directory}/ops-insert.svg",
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

    for key in error_dfs:
        if error_dfs[key]['instance_id'].count() > 0:
            plot(
                error_dfs[key],
                f"{directory}/errors_{key}.svg",
                figsize=(12,5),
                x="instance_id",
                y="count",
                hue=None,
                x_label="errors",
                y_label="count",
                title=f"Number of errors in {key}",
            )

    for key in dfs:
        plot(
            dfs[key],
            f"{directory}/instances_overall-runtime_{key}.svg",
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
