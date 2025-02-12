from fasthtml.common import *
from optimum.pipelines import pipeline

classifier = pipeline(task="text-classification", accelerator="ort",
                      model = "cointegrated/rubert-tiny-sentiment-balanced",
                      truncation=True,
                      device='cpu')

app, rt = fast_app()

@rt('/api/classify')
def get(text: str):
    print(text)
    res = classifier(text)
    print(res)
    return res[0]


@rt('/api/classify/many')
def post(data: dict):
    texts = data['text']
    print("Starting classification, size:", len(texts))
    res = classifier(texts)
    return {'result': res}
    

serve(port=5002, reload=False)