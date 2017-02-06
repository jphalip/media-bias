This repository contains all the code I wrote to support a case study published on my blog: 

The study aims to evaluate bias in the media using sentiment analysis of video titles published by some prominent
American TV channels on their Youtube accounts.

Setup
=====

A bit of setting up is required before you can run this code.

Google API key
--------------

First, you need to get an API key from Google by following the steps described here: https://developers.google.com/api-client-library/python/guide/aaa_apikeys
 
This key will be used for two services:
  - Google Cloud Natural Language API
  - YouTube Data API v3

Once you've acquired a key, save it into a file named `google-api-key.txt` at the root of this repository.

Python environment
------------------

The following Python packages need to be installed in your Python environment:

	ipython==5.1.0
	pandas==0.19.1
	google-api-python-client==1.5.5
	unicodecsv==0.14.1

Acquiring data
==============

Four types of datasets must be generated: channels, topics, videos and sentiment scores.

Channels
--------

Create a `channels.csv` file using the structure detailed in this example:

```python
channels = pandas.DataFrame.from_records([
    {'title': 'Fox News', 'slug': 'fox-news', 'youtube_id': 'UCXIJgqnII2ZOINSWNOGFThA', 'playlist_id': 'UUXIJgqnII2ZOINSWNOGFThA', 'url': 'https://www.youtube.com/user/FoxNewsChannel', 'color': '#5975a4'},
    {'title': 'CNN', 'slug': 'cnn', 'youtube_id': 'UCupvZG-5ko_eiXAupbDfxWw', 'playlist_id': 'UUupvZG-5ko_eiXAupbDfxWw', 'url': 'https://www.youtube.com/user/CNN', 'color': '#b55d60'},
    {'title': 'MSNBC', 'slug': 'msnbc', 'youtube_id': 'UCaXkIU1QidjPwiAYu6GcHjg', 'playlist_id': 'UUaXkIU1QidjPwiAYu6GcHjg', 'url': 'https://www.youtube.com/user/msnbcleanforward', 'color': '#5f9e6e'},
    {'title': 'CBS News', 'slug': 'cbs-news', 'youtube_id': 'UC8p1vwvWtl6T73JiExfWs1g', 'playlist_id': 'UU8p1vwvWtl6T73JiExfWs1g', 'url': 'https://www.youtube.com/user/CBSNewsOnline', 'color': '#666666'},
])

channels.to_csv('channels.csv', index=False, encoding='utf-8')
```

The `youtube_id` is the channel's unique Youtube ID. Finding out a channel's ID is a little tricky:

- Go to the channel's page (e.g. https://www.youtube.com/user/CNN)
- View the HTML source of the page.
- Look for "data-channel-external-id" in the HTML source. The value associated with it is the channel's Youtube ID.

The `playlist_id` corresponds to a channel's default playlist where all its videos are published. To retrieve a channel's `playlist_id`:
- Visit this url after replacing "CHANNEL-ID" with the channel's ID: https://developers.google.com/apis-explorer/#search/youtube/youtube/v3/youtube.channels.list?part=contentDetails&id=CHANNEL-ID
- Click the "Execute without OAuth" link at the bottom of the page.
- The playlist ID is now presented in the field `items[0].contentDetails.relatedPlaylists.uploads`

Topics
------

Create a `topics.csv` file using the structure detailed in this example:

```python
topics = pandas.DataFrame.from_records([
    {'title': 'Obama', 'slug': 'obama', 'variant1': 'Obama', 'variant2': 'Obamas'},
    {'title': 'Clinton', 'slug': 'clinton','variant1': 'Clinton', 'variant2': 'Clintons'},
    {'title': 'Trump', 'slug': 'trump','variant1': 'Trump', 'variant2': 'Trumps'},
    {'title': 'Democrats', 'slug': 'democrats', 'variant1': 'Democrat', 'variant2': 'Democrats'},
    {'title': 'Republicans', 'slug': 'republicans', 'variant1': 'Republican', 'variant2': 'Republicans'},
    {'title': 'Liberals', 'slug': 'liberals', 'variant1': 'Liberal', 'variant2': 'Liberals'},
    {'title': 'Conservatives', 'slug': 'conservatives', 'variant1': 'Conservative', 'variant2': 'Conservatives'},
])

topics.to_csv('topics.csv', index=False, encoding='utf-8')
```

The variants are the different terms that will be searched for in the video titles in order to match videos with your topics of choice.

Videos
------

Run the following snippets of code in order to download all the video metadata from Youtube for your channels of choice:

First, this will download all video information and create a separate CSV file for each channel (e.g. `videos-cnn.csv`):

```python
from code.youtube_api import download_channels_videos

download_channels_videos(channels)
```

Second, this will merge all the CSV files generated above into a single `videos-MERGED.csv` file.

```python
from code.youtube_api import merge_channel_videos
merge_channel_videos(channels)
```

Lastly, this will create extra columns for each topic:

```python
from code.utils import create_topic_columns

videos = pd.read_csv('videos-MERGED.csv')
create_topic_columns(videos, topics)
videos.to_csv('videos.csv', index=False, encoding='utf-8')
```

You now have a `videos.csv` file containing all the video metadata for all channels.

Sentiment scores
----------------

The last step is to download sentiment scores from the Google Natural Language API. **Note that this API is not free.**
Make sure to first refer to the API's [pricing page](https://cloud.google.com/natural-language/pricing) for adequate budgeting.

Run the following:

```python
from code.language_api import download_sentiments

download_sentiments(videos)
```

You now have a `sentiments.csv` file containing the sentiment scores for all relevant videos.

Exploring and analysing the data
================================

Coming soon...