from fasthtml.common import *
import httpx
from pathlib import Path
import pandas as pd

upload_dir = Path("filez")
upload_dir.mkdir(exist_ok=True)
uploaded_data = {}


hdrs = [
    Style('''
          table {
    width: 100%;
    table-layout: fixed;
}

td, th {
    word-wrap: break-word; /* Breaks long words and wraps them */
    overflow-wrap: break-word; /* Same as word-wrap for better compatibility */
    white-space: normal; /* Allows text to wrap */
}
          ''')
]

app, rt = fast_app(hdrs=hdrs)


@rt('/')
def index():
    return Titled("Demo app",
                  ClassifyForm(),
                  P("Upload excel table"),
                  Article(
                      Div(Form(hx_post=upload, hx_target="#table-container", enctype="multipart/form-data")(
                          Input(type="file", name="file", accept=".xlsx"),
                          Button("Upload", type="submit"),
                          style="display: flex;"
                      )),
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

    return render_table(df, 0)


def render_rows(df, page):
    page_size = 30
    start = page * page_size
    end = start + page_size

    rows = []
    for _, row in df.iloc[start:end].iterrows():
        rows.append(Tr(*[Td(str(value)) for value in row.values]))

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


def render_table(df, page):
    rows = render_rows(df, page)
    return Table(
        Thead(Tr(*[Th(col) for col in df.columns])),
        Tbody(*rows)
    )


@rt('/load-more')
def get(request):
    page = int(request.query_params.get('page', 0))
    return render_rows(uploaded_data['dataframe'], page)


def ClassifyForm():
    return Div(
        Textarea(id='search', type="search", name='text',
              placeholder="Enter your text",
              hx_trigger="search, keyup delay:300ms changed",
              hx_get="/classify",
              hx_target="#target", hx_swap="innerHTML",
              style='border-radius: 10px;'),
        Div(id='target')
    )

from bs4 import BeautifulSoup


def clean_html(content):
    if isinstance(content, str):
        # Use BeautifulSoup to remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()
    return content  # Return as is if not a string


@rt('/classify')
async def get(text: str):
    text = clean_html(text)
    print(text)
    url = "http://127.0.0.1:5002/api/classify"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"text": text})
        response = response.json()
    print(response)
    return Div(
        P("Sentiment: ", B(response['label']), Br(), "Probability:", B(f"{response['score']:.2f}"), id="result")
    )


serve()
