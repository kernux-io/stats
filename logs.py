import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import seaborn as sns
import sys
from datetime import datetime, timedelta
from itertools import zip_longest as izip_longest


tab='\t'

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)

def fix_size(value): # Turn into MB
    if "MiB" in value:
        value = float(value.replace('MiB', '')) * 1048576
    elif "MB" in value:
        value = float(value.replace('MB', '')) * 1000000
    elif "KiB" in value:
        value = float(value.replace('KiB', '')) * 1024
    elif "kB" in value or "k" in value:
        value = float(value.replace('kB', '')) * 1000
    elif 'B' in value:
        value = float(value.replace('B', ''))
    return value / 1000000


# Get the start/stop times
def get_start_stop_timestamp(directory, sub_dir):
    data_dir = f"{directory.replace('logs', 'data')}/{sub_dir}"
    with open(f"{data_dir}/start_stop.txt", 'r') as file:
        rows = file.readlines()
        if len(rows) != 2:
            print(f"Only missing timestamp from start/stop for: {data_dir}")
            sys.exit()
        start_time = (datetime.strptime(rows[0].replace('”', '').replace('"', '').replace('\n', ''), "%H:%M:%S") + timedelta(hours=1) - timedelta(seconds=10)).strftime("%H:%M:%S")
        stop_time = (datetime.strptime(rows[1].replace('”', '').replace('"', '').replace('\n', ''), "%H:%M:%S") + timedelta(hours=1) + timedelta(seconds=10)).strftime("%H:%M:%S")
    return start_time, stop_time


# Slice the file between start/stop
def slice_file(filename, start_time, stop_time, keywords):
    start_active = False
    stop_active = False

    with open(filename, 'r') as fr:
        lines = fr.readlines()
        with open(filename, 'w') as fw:
            for line in lines:
                hhmmss = None
                if line.count(':') == 2 and len(line) == 9:
                    hhmmss = line.replace('\n', '').split(':')
                elif line.split(' ')[0].count(':') == 2:
                    hhmmss = line.split(' ')[0].split(':')

                if hhmmss is not None:
                    date_line = 2 if hhmmss[0] == "00" else 1
                    d_line = datetime(2022, 5, date_line, int(hhmmss[0]), int(hhmmss[1]), int(hhmmss[2]))
                    
                    hhmmss_start = start_time.split(':')
                    date_start = 2 if hhmmss_start[0] == "00" else 1
                    d_start = datetime(2022, 5, date_start, int(hhmmss_start[0]), int(hhmmss_start[1]), int(hhmmss_start[2]))

                    hhmmss_stop = stop_time.split(':')
                    date_stop = 2 if hhmmss_stop[0] == "00" else 1
                    d_stop = datetime(2022, 5, date_stop, int(hhmmss_stop[0]), int(hhmmss_stop[1]), int(hhmmss_stop[2]))

                    if d_start < d_line:
                        start_active = True
                    if d_stop < d_line:
                        stop_active = True
                
                    l = line.replace('\n', '')
                    #print(f"{d_start} / {d_stop} | {start_active} / {stop_active} | {l}")

                if start_active and not stop_active and all(keyword not in line for keyword in keywords):
                    #print(f"{all(keyword not in line for keyword in keywords)} / {keywords} | {line}")
                    fw.write(line)


# 'free'
def build_free(directory, sub_dir, start_time, stop_time):
    data = {}
    filename = f"{directory}/{sub_dir}-free.txt"

    if os.path.isfile(filename):
        slice_file(filename, start_time, stop_time, ["total"])
        
        with open(filename, 'r') as f:
            for lines in grouper(f, 3, ''):
                timestamp = lines[0].replace('\n', '')
                mem = ' '.join(lines[1].replace('\n', '').split()).replace('Mem: ', '').split(' ')
                swap = ' '.join(lines[2].replace('\n', '').split()).replace('Swap: ', '').split(' ')

                mem_total = mem[0]
                mem_used = mem[1]
                mem_free = mem[2]
                mem_shared = mem[3]
                mem_cache = mem[4]
                mem_available = float(mem[5])
                swap_total = swap[0]
                swap_used = swap[1]
                swap_free = swap[2]

                if "timestamp" not in data.keys():
                    data["timestamp"] = [timestamp]
                    data["mem_total"] = [mem_total]
                    data["mem_used"] = [mem_used]
                    data["mem_free"] = [mem_free]
                    data["mem_shared"] = [mem_shared]
                    data["mem_cache"] = [mem_cache]
                    data["mem_available"] = [mem_available*0.001024] # Kikibyte to MB
                    data["swap_total"] = [swap_total]
                    data["swap_used"] = [swap_used]
                    data["swap_free"] = [swap_free]
                else:
                    data["timestamp"].append(timestamp)
                    data["mem_total"].append(mem_total)
                    data["mem_used"].append(mem_used)
                    data["mem_free"].append(mem_free)
                    data["mem_shared"].append(mem_shared)
                    data["mem_cache"].append(mem_cache)
                    data["mem_available"].append(mem_available*0.001024) # Kikibyte to MB
                    data["swap_total"].append(swap_total)
                    data["swap_used"].append(swap_used)
                    data["swap_free"].append(swap_free)
                
    df = pd.DataFrame.from_dict(data)
    df.to_csv(f"{directory}/df-free_{sub_dir}.csv", header=True)

    return df


# 'ps'
def build_ps(directory, sub_dir, start_time, stop_time):
    data = {}
    filename = f"{directory}/{sub_dir}-ps.txt"

    if os.path.isfile(filename):
        slice_file(filename, start_time, stop_time, ["PID", "grep"])
        
        with open(filename, 'r') as fr:
            instances = int(filename.split('/')[1].split('_')[0].replace('i', ''))
            if "docker" in filename:
                instances = 9 # TODO

            for lines in grouper(fr, 1 + instances, ''):
                assert len(lines) == 1 + instances
                timestamp = lines[0].replace('\n', '')
                values = re.sub(' +', ' ', lines[1].replace('\n', '')).strip().split(' ')

                for line in lines[1:]:
                    values = re.sub(' +', ' ', line.replace('\n', '')).lstrip(' ').split(' ')
                    if len(values) > 1:
                        if "timestamp" not in data.keys():
                            data["timestamp"]   = [timestamp]
                            data["user"]        = [values[0]]
                            data["pid"]         = [values[1]]
                            data["cpu"]         = [values[2]]
                            data["mem"]         = [values[3]]
                            data["vsz"]         = [values[4]]
                            data["rss"]         = [float(values[5])/1000] # Turn into MB
                            data["tty"]         = [values[6]]
                            data["stat"]        = [values[7]]
                            data["start"]       = [values[8]]
                            data["time"]        = [values[9]]
                            data["cmd"]         = [values[10]]
                        else:
                            data["timestamp"].append(timestamp)
                            data["user"].append(values[0])
                            data["pid"].append(values[1])
                            data["cpu"].append(values[2])
                            data["mem"].append(values[3])
                            data["vsz"].append(values[4])
                            data["rss"].append(float(values[5])/1000) # Turn into MB
                            data["tty"].append(values[6])
                            data["stat"].append(values[7])
                            data["start"].append(values[8])
                            data["time"].append(values[9])
                            data["cmd"].append(values[10])

    df = pd.DataFrame.from_dict(data)
    df.to_csv(f"{directory}/df-ps_{sub_dir}.csv", header=True)

    return df


# 'vmstat'
def build_vmstat(directory, sub_dir, start_time, stop_time):
    data = {}
    filename = f"{directory}/{sub_dir}-vmstat.txt"

    if os.path.isfile(filename):
        slice_file(filename, start_time, stop_time, ["-memory-", " r  b   swpd"])

        with open(filename, 'r') as fr:
            for lines in grouper(fr, 2, ''):
                timestamp = lines[0].replace('\n', '')
                values = re.sub(' +', ' ', lines[1].replace('\n', '')).strip().split(' ')
                
                procs_r = values[0]
                procs_b = values[1]
                mem_swpd = values[2]
                mem_free = values[3]
                mem_buff = values[4]
                mem_cache = values[5]
                swap_si = values[6]
                swap_so = values[7]
                io_bi = values[8]
                io_bo = values[9]
                sys_in = values[10]
                sys_cs = values[11]
                cpu_us = values[12]
                cpu_sy = values[13]
                cpu_id = values[14]
                cpu_wa = values[15]
                cpu_st = values[16]

                if "timestamp" not in data.keys():
                    data["timestamp"] = [timestamp]
                    data["procs_r"] = [procs_r]
                    data["procs_b"] = [procs_b]
                    data["mem_swpd"] = [mem_swpd]
                    data["mem_free"] = [float(mem_free) / 1000] # kilobyte -> MB
                    data["mem_buff"] = [mem_buff]
                    data["mem_cache"] = [mem_cache]
                    data["swap_si"] = [swap_si]
                    data["swap_so"] = [swap_so]
                    data["io_bi"] = [io_bi]
                    data["io_bo"] = [io_bo]
                    data["sys_in"] = [sys_in]
                    data["sys_cs"] = [sys_cs]
                    data["cpu_us"] = [cpu_us]
                    data["cpu_sy"] = [cpu_sy]
                    data["cpu_id"] = [cpu_id]
                    data["cpu_wa"] = [cpu_wa]
                    data["cpu_st"] = [cpu_st]
                else:
                    data["timestamp"].append(timestamp)
                    data["procs_r"].append(procs_r)
                    data["procs_b"].append(procs_b)
                    data["mem_swpd"].append(mem_swpd)
                    data["mem_free"].append(float(mem_free) / 1000) # kilobyte -> MB
                    data["mem_buff"].append(mem_buff)
                    data["mem_cache"].append(mem_cache)
                    data["swap_si"].append(swap_si)
                    data["swap_so"].append(swap_so)
                    data["io_bi"].append(io_bi)
                    data["io_bo"].append(io_bo)
                    data["sys_in"].append(sys_in)
                    data["sys_cs"].append(sys_cs)
                    data["cpu_us"].append(cpu_us)
                    data["cpu_sy"].append(cpu_sy)
                    data["cpu_id"].append(cpu_id)
                    data["cpu_wa"].append(cpu_wa)
                    data["cpu_st"].append(cpu_st)

    df = pd.DataFrame.from_dict(data)
    df.to_csv(f"{directory}/df-vmstat_{sub_dir}.csv", header=True)

    return df


def docker_stats(directory, start_time, stop_time):
    data = {}
    filename = f"{directory}/docker-stats.txt"

    if os.path.isfile(filename):
        slice_file(filename, start_time, stop_time, [])

        with open(filename, 'r') as fr:
            rows = fr.readlines()
            for row in rows:
                row = row.split(' ')
                ts = row[0]
                for i in range(17, len(row), 14):
                    values = row[i:i+14]
                    if len(values) == 14 and len(values[0]) == 12:
                        if "timestamp" not in data.keys():
                            data["timestamp"]       = [ts]
                            data["CONTAINER ID"]    = [values[0]]
                            data["source"]          = [values[1]]
                            data["id"]              = [int(values[1].split('_')[-1])]
                            data["CPU (%)"]         = [values[2].replace('%', '')]
                            data["MEM USAGE"]       = [fix_size(values[3])]
                            data["LIMIT"]           = [fix_size(values[5])]
                            data["MEM %"]           = [values[6]]
                            data["NET IN"]          = [fix_size(values[7])]
                            data["NET OUT"]         = [fix_size(values[9])]
                            data["BLOCK IN"]        = [fix_size(values[10])]
                            data["BLOCK OUT"]       = [fix_size(values[12])]
                            data["PIDS"]            = [values[13].replace('\n', '')]
                        else:
                            data["timestamp"].append(ts)
                            data["CONTAINER ID"].append(values[0])
                            data["source"].append(values[1])
                            data["id"].append(int(values[1].split('_')[-1]))
                            data["CPU (%)"].append(values[2].replace('%', ''))
                            data["MEM USAGE"].append(fix_size(values[3]))
                            data["LIMIT"].append(fix_size(values[5]))
                            data["MEM %"].append(values[6])
                            data["NET IN"].append(fix_size(values[7]))
                            data["NET OUT"].append(fix_size(values[9]))
                            data["BLOCK IN"].append(fix_size(values[10]))
                            data["BLOCK OUT"].append(fix_size(values[12]))
                            data["PIDS"].append(values[13].replace('\n', ''))

    df = pd.DataFrame.from_dict(data)
    df.to_csv(f"{directory}/df-stats_docker.csv", header=True)

    return df


def plot(df, x, y, filename, title, figsize=(5,5), start_time=None, stop_time=None, hue=None, show_fig=False, x_label=None, y_label=None, tick_factor=10, legend=None, ymin=None, ymax=None):
    plt.figure(figsize=figsize)
    ax = sns.lineplot(data=df, x=x, y=y, hue=hue)
    ax.set_xlabel(x_label, fontsize = 8)
    ax.set_ylabel(y_label, fontsize = 8)
    ax.set_title(title, fontsize = 15)
    if ymin is not None and ymax is not None:
        plt.ylim(ymin, ymax)

    # Avoid duplicated ticks on the x axis
    max = str(df[x].max())
    ticks = list(df[x])
    if ":" not in max:
        nums = range(0,int(max))
        ticks = list(nums)
    tick_factor = int(len(ticks) * 0.05)
    #plt.xticks([ticks[i] for i in range(len(ticks)) if i % tick_factor == 0], rotation='vertical')

    # Set legend outside
    if legend is None:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    else:
        ax.legend(loc=legend)

    if show_fig:
        plt.show()
    
    fig = ax.get_figure()
    fig.savefig(filename)


def main(directory=None):
    sub_dirs = [
        "docker",
        "unikernel_allocpool", 
        "unikernel_base",
        "unikernel_dce",
        "unikernel_dce-allocpool",
        "unikernel_falloc",
        "unikernel_fbuddyalloc",
    ]

    # docker-stats
    start_time, stop_time = get_start_stop_timestamp(directory, "docker")
    df_stats = docker_stats(directory, start_time, stop_time)
    df_stats = df_stats.sort_values(by=['timestamp', 'id']).reset_index(drop=True)
    print(df_stats)
    df_plot = df_stats[["timestamp", "MEM USAGE", "source"]]
    plot(df_plot, "timestamp", "MEM USAGE", filename=f"{directory}/stats-docker.svg", title="docker - stats", start_time=start_time, stop_time=stop_time, hue="source", show_fig=True, x_label="timestamp", y_label="MB")

    dfs_free = []
    dfs_ps = []
    dfs_vmstat = []
    for sub_dir in sub_dirs:
        start_time, stop_time = get_start_stop_timestamp(directory, sub_dir)
        print(f"{sub_dir} | {start_time} {stop_time}")

        # free
        df_free = build_free(directory, sub_dir, start_time, stop_time)
        df_free["source"] = sub_dir
        df_free["row_count"] = df_free.reset_index().index
        df_free['mem_available'] = df_free['mem_available'].astype(float)
        df_plot = df_free[["timestamp", "mem_available", "source"]]
        print(df_free)
        plot(df_plot, "timestamp", "mem_available", filename=f"{directory}/free-{sub_dir}.svg", title=f"{sub_dir} - free", start_time=start_time, stop_time=stop_time, show_fig=True, x_label="timestamp", y_label="MB")
        dfs_free.append(df_free)

        # ps
        if sub_dir != "docker":
            df_ps = build_ps(directory, sub_dir, start_time, stop_time)
            df_ps["source"] = sub_dir
            df_ps["row_count"] = df_ps.reset_index().index
            print(df_ps)
            df_ps['rss'] = df_ps['rss'].astype(float)
            df_plot = df_ps[["timestamp", "rss", "pid", "source"]]
            plot(df_plot, "timestamp", "rss", filename=f"{directory}/ps-{sub_dir}.svg", title=f"{sub_dir} - ps", start_time=start_time, stop_time=stop_time, hue="pid", show_fig=True, x_label="timestamp", y_label="MB")
            print(df_ps)
            dfs_ps.append(df_ps)
        
        # vmstat
        df_vmstat = build_vmstat(directory, sub_dir, start_time, stop_time)
        df_vmstat["source"] = sub_dir
        df_vmstat["row_count"] = df_vmstat.reset_index().index
        df_vmstat['mem_free'] = df_vmstat['mem_free'].astype(float)
        print(df_vmstat)
        df_plot = df_vmstat[["timestamp", "mem_free", "source"]]
        plot(df_plot, "timestamp", "mem_free", filename=f"{directory}/vmstat-{sub_dir}.svg", title=f"{sub_dir} - vmstat", start_time=start_time, stop_time=stop_time, show_fig=True, x_label="timestamp", y_label="MB")
        dfs_vmstat.append(df_vmstat)
    
    # docker-stats
    df_stats = df_stats.groupby(['timestamp'])['MEM USAGE'].sum().reset_index()
    df_stats["row_count"] = df_stats.reset_index().index + 1
    df_stats["source"] = "docker"
    df_stats = df_stats.rename({'MEM USAGE': 'rss'}, axis='columns')
    df_plot = df_stats[["row_count", "rss", "source"]]
    print(df_plot)
    plot(df_plot, "row_count", "rss", filename=f"{directory}/stats-docker-merged.svg", title="docker - stats", start_time=start_time, stop_time=stop_time, show_fig=True, x_label="timestamp", y_label="MB")

    # free
    df_free_union = pd.concat(dfs_free, ignore_index=True)
    df_plot = df_free_union[["row_count", "mem_available", "source"]]
    plot(df_plot, "row_count", "mem_available", filename=f"{directory}/free.svg", title="free", start_time=None, stop_time=None, hue="source", show_fig=True, x_label="seconds", y_label="MB")
    
    # ps
    df_ps_union = pd.concat(dfs_ps, ignore_index=True)
    df_ps_union.timestamp = df_ps_union.timestamp.apply(lambda ts: f"24:{ts.split(':')[1]}:{ts.split(':')[2]}" if ts.startswith('00') else ts)
    df_ps_union = df_ps_union.groupby(['timestamp', 'source'])['rss'].sum().reset_index()
    df_ps_union['row_count'] = df_ps_union.groupby('source').cumcount() + 1
    print(df_ps_union)
    print(df_ps_union['source'].value_counts())
    df_plot = df_ps_union[["row_count", "rss", "source"]]
    plot(df_plot, "row_count", "rss", filename=f"{directory}/ps.svg", title="ps", start_time=None, stop_time=None, hue="source", show_fig=True, x_label="seconds", y_label="MB")

    # vmstat
    df_vmstat_union = pd.concat(dfs_vmstat, ignore_index=True)
    df_plot = df_vmstat_union[["row_count", "mem_free", "source"]]
    plot(df_plot, "row_count", "mem_free", filename=f"{directory}/vmstat.svg", title="vmstat", start_time=None, stop_time=None, hue="source", show_fig=True, x_label="seconds")

    dir_split = directory.split('/')[1].split('_')
    instances = dir_split[0]
    memory = dir_split[1]

    # JOIN DOCKER-STATS & PS
    df_ps_union = df_ps_union[["row_count", "rss", "source"]]
    df_stats = df_stats[["row_count", "rss", "source"]]
    df = pd.concat([df_stats, df_ps_union], ignore_index=True)
    df = df.sort_values(by=['source', 'row_count']).reset_index(drop=True)
    print(df)
    plot(df, "row_count", "rss", filename=f"{directory}/memory_{instances}{memory}.svg", title="", start_time=None, stop_time=None, hue="source", legend='center right', show_fig=True, x_label="seconds", y_label="MB")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="calculate some statistics on the benchmark results")
    parser.add_argument('-d', '--directory', required=True, help="specify the input directory")
    args = parser.parse_args()
    main(directory=args.directory)
