# Fink MLflow controller

Use this repository to manage MLflow instance. You would simply clone it to the machine, and install it:

```bash
git clone https://github.com/JulienPeloton/fink-mlflow-controller
cd fink-mlflow-controller
pip install .
```

## Local accounts

Use the controller to manage user accounts:

```bash
$ fink_mlflow -h
usage: fink_mlflow [-h] {create,delete,list} ...

positional arguments:
  {create,delete,list}
    create              Create a user
    delete              Delete a user
    list                List users

options:
  -h, --help            show this help message and exit
```
