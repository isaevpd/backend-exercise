# Exercise


A backend exercise.

The purpose of the exercise is demonstrate usage of basic Python skills

For the backend use Flask to implement a basic Flask API  with
a bit of functionality.

## The Problem

As a race managers we want to be able to post finished race results.
Race results are name of the race, date, and list of drivers and number of points
they made.
As a race viewers we want to be able to get specific race results
As a race viewers we want to be able to get driver or team standings
after all completed races

### Backend

Create an API for team resource
Create an API for driver resource
Create an API for race resource
APIs should support basic filtering(e.g. by country, name and etc)

Data for the drivers and teams is provided in the `data/` folder.

## Tips to get started

Install python in your system.

Install virtualenv for python https://pypi.python.org/pypi/virtualenv. This
step is optional but recommended, since it won't make available globally Flask
to your system, but only for this project. If not using virtualenv you can just
run:

    easy_install Flask

or

    pip install Flask

If using virtualenv, create a virtual environment in the cloned project folder.
Call it `env`:

    virtualenv env

Activate the virtual environment you will have to do this every time you get
back to the project:

    source env/bin/activate

Install the dependencies for the project:

    pip install -r requirements.txt

to run the app just do

    python app.py

the Flask server (in debug mode) will be running in port 5000. It loads in
its root the base HTML file to build on.

All yours, have fun!


PS: I have no idea of Formula1 or racing, just felt easy to propose a problem
and find real data for the examples.
