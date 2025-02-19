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


## Build and run docker image for contest
To build an image run
```sh
docker build -f contest/Dockerfile -t ailab_itmo:latest .
```

To run this, put `data.csv` file into `contest` folder and run 
linux
```sh
docker run -v $(pwd)/contest/data.csv:/contest/data.csv --name my_container ailab_itmo:latest
```
windows
```pwsh
docker run -v ${PWD}/contest/data.csv:/contest/data.csv --name my_container ailab_itmo:latest
```