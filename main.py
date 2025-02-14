from bs4 import BeautifulSoup
from fasthtml.common import *
from monsterui.all import *
import httpx
from pathlib import Path
import pandas as pd
import preprocess

upload_dir = Path("filez")
upload_dir.mkdir(exist_ok=True)
uploaded_data = {}
api_url = "http://127.0.0.1:5002/api"


app, rt = fast_app(hdrs=Theme.blue.headers())


@rt('/')
def index():
    return Titled("Demo app",
                  ThemePicker(color=False, radii=False, shadows=False, font=False, mode=True, cls='p-4'),
                  ClassifyForm(),
                  H3("Upload excel table"),
                  Article(
                      Form(
                          UploadZone(DivCentered(Span("Upload Zone"), UkIcon("upload")), accept=".xlsx", name="file"),
                          Button("Submit", cls=ButtonT.primary),
                          hx_post=upload, hx_target="#table-container", enctype="multipart/form-data",
                          cls=PaddingT.md,
                      ),
                      Div(id="table-container")
                  )
                  )


@rt
async def upload(file: UploadFile):
    # Save the uploaded file
    file_path = upload_dir / file.filename
    filebuffer = await file.read()
    file_path.write_bytes(filebuffer)

    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)
    uploaded_data['dataframe'] = df

    return await render_table(df, 0)


async def classify_many(df: pd.DataFrame, slice: pd.DataFrame):
    df.loc[slice.index, 'Text'] = slice['MessageText'].apply(preprocess.clean_html)
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url + "/classify/many", json={"text": df.loc[slice.index, 'Text'].tolist()})
        res = response.json()['result']
    df.loc[slice.index, 'label'] = [res[i]['label'] for i in range(len(res))]
    df.loc[slice.index, 'score'] = [res[i]['score'] for i in range(len(res))]
    return df.loc[slice.index]


def to_repr(value, col):
    if col == 'label':
        to_cls = {'negative': 'uk-label-destructive', 'positive': LabelT.primary, 'neutral': LabelT.secondary}
        return Span(value, cls=('uk-label', to_cls[value]))
    if isinstance(value, float): return f"{value:.3f}"
    return str(value)


async def render_rows(df: pd.DataFrame, page):

    page_size = 30
    start = page * page_size
    end = start + page_size

    rows = []
    slice = await classify_many(df, df.iloc[start:end])
    for _, row in slice.iterrows():
        rows.append(Tr(*[Td(to_repr(value, col), style='max-width: 400px; word-wrap: break-word;')
                         for value, col in zip(row.values, df.columns)]))

    # Add the HTMX infinite scroll row if there is more data to load
    if end < len(df):
        rows.append(
            Tr(
                Td('Loading...', colspan=len(df.columns)),
                hx_get=f"/load-more?page={page + 1}",
                hx_trigger="revealed",
                hx_swap="afterend",
            )
        )

    return rows

# Function to render the full table


async def render_table(df, page):
    rows = await render_rows(df, page)
    return Table(
        Thead(Tr(*[Th(col) for col in df.columns])),
        Tbody(*rows),
    )


@rt('/load-more')
async def get(request):
    page = int(request.query_params.get('page', 0))
    return await render_rows(uploaded_data['dataframe'], page)


def ClassifyForm():
    return Div(
        LabelTextArea(label="Sentiment samples", id='search', type="search", name='text',
                      placeholder="Enter texts to classify",
                      hx_trigger="search, keyup delay:300ms changed",
                      hx_get="/classify",
                      hx_target="#target", hx_swap="innerHTML",
                      style='border-radius: 10px;'),
        Div(id='target'),
        cls=PaddingT.lg
    )



@rt('/classify')
async def get(text: str):
    text = preprocess.clean_html(text)
    print(text)
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url + "/classify", params={"text": text})
        response = response.json()
    print(response)
    return Div(
        H3("Output"),
        Card(
            P(Span("Sentiment:", cls='pr-4'), to_repr(response['label'], 'label'), Br(),
              Span("Probability:", cls='pr-4'), to_repr(response['score'], 'score'), id="result"),
            cls=('mb-15 mt-5', CardT.hover)
        )
    )


serve()
