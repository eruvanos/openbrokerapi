# Development commands and notes

## Test
```
./setup.py test
```

## Register
```
./setup.py register
./setup.py register -r testpypi
```

## Upload
```
./setup.py register sdist upload
./setup.py register sdist upload -r testpypi
```

## Install from testpypi
```
pip install -i https://testpypi.python.org/simple openbrokerapi
```

