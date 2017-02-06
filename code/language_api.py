import os
import time
import json
import unicodecsv as csv
from apiclient.discovery import build
from apiclient.errors import HttpError


API_KEY = open('google-api-key.txt', 'r').read()
language_service = build('language', 'v1', developerKey=API_KEY)


def analyze_sentiment(text):
    """
    Sends a request to the Google Natural Language API to analyze
    the sentiment of the given piece of text.
    """
    request = language_service.documents().analyzeSentiment(
      body={
        'document': {
          'type': 'PLAIN_TEXT',
          'content': text,
        }
      })
    return request.execute()


def download_sentiments(videos, output_file='sentiments.csv'):
    """
    Downloads sentiment scores from the Google Natural Language API
    for the given videos, then stores the results in a CSV file.
    """

    # Time to wait when we get rate-limited
    wait_time = 120
    
    # Create new (or open existing) CSV file to hold the sentiment analysis values
    if os.path.isfile(output_file):
        # Open existing file in "append" mode
        f = open(output_file, 'a')
        writer = csv.writer(f, encoding='utf-8')
    else:
        # Open new file in "write" mode and add the headers
        f = open(output_file, 'w')
        writer = csv.writer(f, encoding='utf-8')
        writer.writerow(['youtube_id', 'sentiment', 'sentiment_score', 'sentiment_magnitude'])

    i = 0
    n_videos = videos.shape[0]
    print 'Start processing %s videos...' % n_videos
    while i < n_videos:
        video = videos.iloc[i]
        try:
            # Send request to the Google Natural Language API for the current video
            sentiment = analyze_sentiment(video['title'])
            # Add result to the CSV file
            writer.writerow([
                video['youtube_id'],
                json.dumps(sentiment),
                sentiment['documentSentiment']['score'],
                sentiment['documentSentiment']['magnitude'],
            ])   
            # Move on to the next video
            i += 1
        except HttpError, e:
            if e.resp.status == 429:
                print 'Processed %s/%s videos so far...' % (i, n_videos)
                # We got rate-limited, so wait a bit before trying again with the same video
                time.sleep(wait_time)
            elif e.resp.status == 400:
                # Bad request. Probably something wrong with the video's text
                error_content = json.loads(e.content)['error']
                print 'Error [%s] for video %s: %s' % (
                    error_content['code'], video['youtube_id'], error_content['message'])
                # Move on to the next video
                i += 1
            else:
                print "Unhandled error for video %s: %s" % (
                    video['youtube_id'], video['title'])
                raise
    f.close()
    print 'Finished processing %s videos.' % n_videos