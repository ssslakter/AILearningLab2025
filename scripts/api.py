import sys
sys.path.append(".")
from fasthtml.common import *
from src.preprocess import clean_html
import pandas as pd
from pathlib import Path
from src.benchmark import *
from optimum.pipelines import pipeline

classifier = pipeline(task="text-classification", accelerator="ort",
                      model = 'clapAI/modernBERT-base-multilingual-sentiment',
                      truncation=True,
                      device='cpu')

app, rt = fast_app()

@rt('/api/classify')
def post(text: str):
    text = clean_html(text)
    print(text)
    res = classifier(text)
    print(res)
    return res[0]


@rt('/api/benchmark')
def post(filename: str): 
    df = pd.read_excel(Path('filez')/filename)
    texts = df['Text'].to_list()
    lengths, times = benchmark(classifier, texts)
    print(lengths)
    print(times)
    return to_mpl(lengths, times)


@rt('/api/classify/many')
def post(data: dict):
    texts = data['text']
    print("Starting classification, size:", len(texts))
    res = classifier(texts)
    return {'result': res}
    

serve(port=5002, reload=False)