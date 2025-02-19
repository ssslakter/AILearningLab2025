import pandas as pd
from bs4 import BeautifulSoup

def clean_html(content):
    if isinstance(content, str):
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()
    return content  # Return as is if not a string

def preprocess_data(df: pd.DataFrame):
    df['Text'] = df['MessageText'].apply(clean_html)
    if 'Class' in df.columns:
        df['label'] = df['Class'].apply(lambda x: {'B': 'negative', 'G': 'positive', 'N': 'neutral'}[x])
    return df

def postprocess_labels(labels):
    fn = {'negative': 'B', 'positive': 'G', 'neutral': 'N'}
    return [fn[l] for l in labels]