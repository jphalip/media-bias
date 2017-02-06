from __future__ import division
import math
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns


def plot_channel_stats(stats, topics, channels, fig_height=8, y_center=False, title=None):
    """
    Plots bar charts for the given channel stats.
    A separate subplot is generated for each given topic.
    """
    fig, axes = plt.subplots(nrows=int(math.ceil(topics.shape[0]/2)), ncols=2, figsize=(8,fig_height))
    fig.subplots_adjust(hspace=.5)
    
    for i, topic in topics.iterrows():
        ax = fig.axes[i]
        
        # If requested, center all axes around 0
        if y_center:
            # Calculate the approximate amplitude of the given stats values
            amplitude = math.ceil(stats.abs().values.max()*10)/10
            ax.set_ylim(-amplitude, amplitude)
        
        # If we have negative values, grey out the negative space for better contrast
        if stats.values.min() < 0:
            ax.axhspan(0, ax.get_ylim()[0], facecolor='0.2', alpha=0.15)
        
        color = channels.sort_values('title').color
        ax.bar(range(len(stats.index)), stats[topic.slug], tick_label=stats.index, color=color, align='center')
        ax.set_title(topic.title, size=11)
        
    # Hide potential last empty subplot
    if topics.shape[0] % 2:
        fig.axes[-1].axis('off')

    # Optional title at the top
    if title is not None:
        multiline = '\n' in title
        y = 1. if multiline else .96
        plt.suptitle(title, size=14, y=y)
        
    plt.show()

    
def plot_compressed_channel_stats(stats, color=None, y_center=False, title=None):
    """
    Similar to plot_channel_stats except everything is represented
    in a single plot (i.e. no subplots).
    """
    plt.figure(figsize=(6,4))
    ax = plt.gca()
    
    # If requested, center all axes around 0
    if y_center:
        # Calculate the approximate amplitude of the given stats values
        amplitude = math.ceil(stats.abs().values.max()*10)/10
        ax.set_ylim(-amplitude, amplitude)

    # If we have negative values, grey out the negative space
    # for better contrast
    if stats.values.min() < 0:
        ax.axhspan(0, ax.get_ylim()[0], facecolor='0.2', alpha=0.15)
        
    # The actual plot
    stats.plot(kind='bar', color=color, width=0.6, ax=ax)
    
    # Presentation cleanup
    plt.xlabel('')
    plt.xticks(rotation=0)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    # Optional title at the top
    if title is not None:
        plt.title(title)

    plt.show()
    
    
def plot_sentiment_series(videos, topics, channels, start_date=None, title=None):
    """
    Plot linear timeseries of sentiment scores for the given videos:
    One separate subplot is generated for each topic. Each subplot
    has one timeseries for each channel, and one timeseries for the
    average values across all channells.
    """
    fig, axes = plt.subplots(nrows=topics.shape[0], ncols=1, figsize=(8,4*topics.shape[0]))
    fig.subplots_adjust(hspace=.3)
    
    # Resample rule: 2-week buckets
    resample_rule = '2W'
    
    # Calculate the approximate amplitude of the given sentiment values
    amplitude = math.ceil(videos.sentiment_score.abs().max()*10)/10
    
    for i, topic in topics.reset_index().iterrows():
        ax = fig.axes[i]
        # Grey out the negative sentiment area
        ax.axhspan(0, -1, facecolor='0.2', alpha=0.15)

        # Plot a timeseries for the average sentiment across all channels
        topic_mask = videos[topic.slug]
        if start_date is not None:
            topic_mask = topic_mask & (videos.published_at >= start_date)
        ts = videos[topic_mask].set_index('published_at').resample(resample_rule)['sentiment_score'].mean().interpolate()
        sns.tsplot(ts, ts.index, color='#fcef99', linewidth=6, ax=ax)
        
        # Plot a separate time-series for each channel
        for _, channel in channels.iterrows():
            channel_mask = topic_mask & (videos.channel==channel.title)
            ts = videos[channel_mask].set_index('published_at').resample(resample_rule)['sentiment_score'].mean().interpolate()
            if len(ts) > 1:
                sns.tsplot(ts, ts.index, color=channel['color'], linewidth=1, ax=ax)

        # Format x-axis labels as dates
        xvalues = ax.xaxis.get_majorticklocs()
        xlabels = [datetime.utcfromtimestamp(x/1e9).strftime("%Y.%m") for x in xvalues]
        ax.set_xticklabels(xlabels)

        # A little extra presentation cleanup
        ax.set_xlabel('')
        ax.set_title(topic['title'], size=11)
        ax.set_ylim(-amplitude,amplitude)

        # Add legend
        handles = [Patch(color='#fcef99', label='Average')]
        for _, channel in channels.iterrows():
            handles.append(Patch(color=channel['color'], label=channel['title']))
        ax.legend(handles=handles, fontsize=8)

    # Optional title at the top
    if title is not None:
        plt.suptitle(title, size=14, y=.92)
        
    plt.show()