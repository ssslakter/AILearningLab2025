from fasthtml.common import *
from optimum.pipelines import pipeline

classifier = pipeline(task="text-classification", accelerator="ort", model = "cointegrated/rubert-tiny-sentiment-balanced", device='cpu')

app, rt = fast_app()

@rt('/api/classify')
def get(text: str):
    print(text)
    res = classifier(text)
    print(res)
    return res[0]

serve(port=5002, reload=False)