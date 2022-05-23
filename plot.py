import argparse
import os
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def read_df(directory, filename):
    path_df = f"{directory}/{filename}"
    if os.path.isfile(path_df) and os.stat(path_df).st_size > 0:
        return pd.read_csv(path_df)


def plot(df, filename, figsize=(5,5), x="observation", y="value", hue="source", x_label="", y_label="", title="", labels=[], rotation=0, legend='best', ymax=None):
    plt.figure(figsize=figsize)
    ax = sns.barplot(x=x, y=y, data=df, ci="sd", capsize=0.05, hue=hue)
    ax.set_xlabel(x_label, fontsize = 8)
    ax.set_ylabel(y_label, fontsize = 8)
    ax.set_title(title, fontsize = 15)
    ax.legend(loc=legend)
    if ymax is not None:
        plt.ylim(0, ymax)
    if rotation != 0:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=rotation, horizontalalignment='right')
    if labels != []:
        ax.set_xticklabels(labels, rotation=rotation)
    plt.show()
    fig = ax.get_figure()
    fig.savefig(filename)


def main(dfs=None, directory=None, sub_dirs=None, error_dfs=None):
    if directory is not None:
        sub_dirs = [
            "docker",
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

    instances = int(directory.split('/')[1].split('i_')[0])
    xdim = 5 if instances <= 5 else instances
    ydim = 5 if instances <= 5 else 5 + (instances/6)
    rotation = 0 if instances < 5 else 45

    # Overall runtime (ms)
    df_plot = df.loc[df["observation"] == "OVERALL, RunTime(ms)"]
    plot(
        df_plot,
        f"{directory}/overall-runtime.svg",
        x_label="",
        y_label="ms",
        title="Overall Runtime",
        labels=["artifacts"],
        legend='lower left',
        ymax=16000,
    )
    
    # Overall throughput (ops/sec)
    df_plot = df.loc[df["observation"] == "OVERALL, Throughput(ops/sec)"]
    plot(
        df_plot,
        f"{directory}/overall-throughput.svg",
        x_label="",
        y_label="sec",
        title="Overall Throughput (ops/sec)",
        labels=["artifacts"],
        legend='lower left',
        ymax=125,
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
        f"{directory}/ops-read.svg",
        figsize=(12,5),
        x_label="",
        y_label="μs",
        title="Read Operations (latency)",
        labels=[
            "average latency",
            "min latency",
            "max latency",
            "95th percentile latency",
            "99th percentile latency"
        ],
        legend='upper left',
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
        f"{directory}/ops-cleanup.svg",
        figsize=(12,5),
        x_label="",
        y_label="μs",
        title="Cleaup Operations (latency)",
        labels=[
            "average latency",
            "min latency",
            "max latency",
            "95th percentile latency",
            "99th percentile latency"
        ],
        legend='lower left',
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
        f"{directory}/ops-insert.svg",
        figsize=(12,5),
        x_label="",
        y_label="μs",
        title="Insert Operations (latency)",
        labels=[
            "average latency",
            "min latency",
            "max latency",
            "95th percentile latency",
            "99th percentile latency"
        ],
        legend='upper left',
    )

    for key in error_dfs:
        if error_dfs[key]['instance_id'].count() > 0:
            plot(
                error_dfs[key],
                f"{directory}/errors_{key}.svg",
                figsize=(xdim,ydim),
                x="instance_id",
                y="count",
                hue=None,
                x_label="instance(s)",
                y_label="count",
                title=f"Errors in {key}",
                rotation=rotation,
                legend='lower left',
                ymax=1,
            )

    for key in dfs:
        plot(
            dfs[key],
            f"{directory}/instances_overall-runtime_{key}.svg",
            figsize=(xdim,ydim),
            x="instance",
            y="OVERALL, RunTime(ms)",
            x_label="instance(s)",
            y_label="ms",
            title="Overall Runtime/Instance",
            rotation=rotation,
            legend='lower left',
            ymax=16000,
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
