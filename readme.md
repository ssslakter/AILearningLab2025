# AI Learning Lab 2025

Install dependencies
```sh
pip install -r requirements.txt
```
To start api and web-server run
```sh
python scripts/api.py
```
```sh
python scripts/main.py
```

### Measure rps
To measure requests per seconds with different number of concurrent requests run:
```sh
python scripts/test_rps.py <length>
```
where `<length>` is how long are sequences in the requests. You can choose `short`, `med` or `long`
