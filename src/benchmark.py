from tqdm.auto import tqdm
import time
import pandas as pd
import numpy as np
from collections import defaultdict
# import plotly.express as px
# from fh_plotly import plotly2fasthtml
from fh_matplotlib import matplotlib2fasthtml


def benchmark(pipe, texts):
    times, lengths = [], []
    for el in tqdm(texts):
        start = time.time()
        pipe(el)
        lengths.append(len(pipe.tokenizer.tokenize(el)))
        end = time.time()
        times.append(end - start)
    return np.array(lengths), np.array(times)


def group_for_plot(lengths, times):
    length_time_map = defaultdict(list)
    for length, time in zip(lengths, times): length_time_map[length].append(time)

    # Calculate averages
    unique_lengths = []
    average_times = []
    for length, time_list in length_time_map.items():
        unique_lengths.append(length)
        average_times.append(np.mean(time_list))

    # Sort for plotting
    sorted_indices = np.argsort(unique_lengths)
    unique_lengths = np.array(unique_lengths)[sorted_indices]
    average_times = np.array(average_times)[sorted_indices]
    return unique_lengths, average_times


@matplotlib2fasthtml
def to_mpl(lengths, times):
    import matplotlib.pyplot as plt
    unique_lengths, average_times = group_for_plot(lengths, times)
    plt.figure(figsize=(9, 4))
    plt.scatter(lengths, times, color='blue', label='Individual Runs', alpha=0.7)
    plt.plot(unique_lengths, average_times, color='red', label='Average Time', linewidth=2)
    plt.xlabel('Sequence Length')
    plt.ylabel('Run Time (s)')
    plt.title('Run Time vs Sequence Length')
    plt.legend()
    plt.grid(True)


# def to_plotly(lengths, times):
#     unique_lengths, average_times = group_for_plot(lengths, times)

#     # Create DataFrame for individual runs
#     df_runs = pd.DataFrame({'Sequence Length': lengths, 'Run Time (s)': times})

#     # Create DataFrame for average times
#     df_avg = pd.DataFrame({'Sequence Length': unique_lengths, 'Average Time (s)': average_times})

#     # Create scatter plot for individual runs and line plot for average times
#     fig = px.scatter(df_runs, x='Sequence Length', y='Run Time (s)', 
#                     color_discrete_sequence=['blue'], opacity=0.7, 
#                     labels={'Run Time (s)': 'Run Time (s)', 'Sequence Length': 'Sequence Length'},
#                     title='Run Time vs Sequence Length')

#     # Add average time line
#     fig.add_scatter(x=df_avg['Sequence Length'], y=df_avg['Average Time (s)'], mode='lines', 
#                     line=dict(color='red', width=2), name='Average Time')

#     # Show grid
#     fig.update_layout(showlegend=True, xaxis=dict(showgrid=True), yaxis=dict(showgrid=True))

#     return fig
