# BDE Flask App

![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/pstjohn/bde_prediction_flask)

The only tricky dependency here is [`rdkit`](http://www.rdkit.org/docs/Install.html), but it can be installed with 
```
conda install -c conda-forge rdkit
```


The dependencies are therefore
* rdkit
* pandas
* seaborn (for colors)
* flask
* wtforms

## To launch a local server:
```
cd bde_prediction
gunicorn --bind 0.0.0.0:2222 main:app
```

Then browse to 0.0.0.0:2222 in a web browser

### Alternatively, with Docker:

```bash
docker build -t bde .
docker run -e PORT=2222 -p 2222:2222 -t bde
```
Then browse to 0.0.0.0:2222 in a web browser
