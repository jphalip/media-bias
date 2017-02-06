import re
import pandas as pd
from IPython.display import HTML


def show_videos(videos, ids, columns=None):
    """
    Shows some basic information about the videos with
    the given youtube IDs. Contrary to the default
    pandas HTML representation, the information is never
    truncated (no max_colwidth limits).
    """
    if columns is None:
        columns = ['title', 'sentiment_score', 'channel', 'published_at', 'youtube_id']
    with pd.option_context('display.max_colwidth', -1):
        return HTML(
            videos[videos.youtube_id.isin(ids)][columns].to_html(index=False)
        )


def get_variants(topic):
    """
    Returns all variants for the given topic.
    """
    return [topic['variant%s'%i] for i in range(1,3) if not pd.isnull(topic['variant%s'%i])]


def get_pattern(topic):
    """
    Compiles and returns the regular expression pattern
    matching all variants of the given topic.
    """
    variants = get_variants(topic)
    sub_patterns = [r'(.*\b)%s\b(.*)' % variant.lower() for variant in variants]
    return re.compile(r'|'.join(sub_patterns), flags=re.IGNORECASE)


def is_relevant(video, topic_pattern):
    """
    Returns True if the given topic is relevant to the given video.
    """
    return bool(topic_pattern.match(video['title']))


def create_topic_columns(videos, topics):
    """
    Creates a separate column in the given `videos` dataframe
    for each given topic. Those columns will contain `True` values
    for videos that mention the corresponding topic.
    Finally creates a `relevant` column that will contain `True`
    for videos that mentions any topic at all.
    """
    
    # Clear values
    videos['relevant'] = False

    # Create masks for each topic so we can later filter videos by topics
    topic_masks = []
    for _, topic in topics.iterrows():
        videos[topic['slug']] = False  # Clear values
        pattern = get_pattern(topic)
        topic_mask = videos.apply(lambda video: is_relevant(video, pattern), axis=1)
        topic_masks.append(topic_mask)
        videos[topic['slug']] = topic_mask

    # Mark video as 'relevant' if it mentions any of the topics
    videos['relevant'] = np.any(np.column_stack(topic_masks), axis=1)
