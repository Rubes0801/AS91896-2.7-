# AS91896-2.7-
Programming Internal. My NZ Wildlife website will be a newer version, with better things such as a more user 
friendly search process, include a new register page and a new login page. This gets the user more 
involved in the website and more interested in what it has to offer.

# Getting started
## Preliminaries
### Enable scripts to run on your machine


```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Create a virtual environment

To install a virtual environment called ".venv"
REM: Remember that a virtual environment creates a small project-specific set of code libraries, which makes them easier to delete and avoids versioning hell, encountered when running multiple projects on one machine.
```
python -m venv .venv
```

## Activate the virtual environment

To activate virtual environment:
NB:  You need the virtual env activate to ensure the libraries are installed here
```
.venv\scripts\activate
```

## Dependency installation

### OPTION A: one-by-one

To install Flask, if not already installed
```
pip install flask
```
### OPTION B: all-in-one

To install all dependencies frOm a requirements file, if provided
NB: If you don't have a requirements file, see 'Extra tasks' below for how to create one
```
pip install -r requirements.txt
```

## Run the app
```
python app.py

pip install gunicorn
```

## Extra tasks           

### Create a requirements file
```
pip freeze > requirements.txt
```