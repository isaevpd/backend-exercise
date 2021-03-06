# -*- coding: utf-8 -*-

import os.path
import json
from flask.ext.api import FlaskAPI, status, exceptions
from flask import request, url_for
from collections import OrderedDict
from datetime import datetime


SRC_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(SRC_DIR, 'data')

app = FlaskAPI(__name__)

teams = json.load(open('data/teams.json'))
drivers = json.load(open('data/drivers.json'))
races = []

# DRIVER_NAMES = [d['driver'] for d in drivers]
# TEAM_NAMES = [t['team'] for t in teams]
DRIVER_FILTER_FIELDS = ['id', 'driver', 'country', 'team']
TEAM_FILTER_FIELDS = ['id', 'team', 'car']
RACE_FILTER_FIELDS = ['race', 'date']


# lets start with a few helper functions
def get_date(s):
    """
    takes a string as an argument and returns a datetime object
    if applicable, else None
    """
    try:
        return datetime.strptime(s, '%Y-%m-%d')
    except ValueError:
        return None


# time to reinvent the wheel
def filter_by_params(dict_list, params):
    """
    simple custom filter function that iterates over each dict in a list
    and checks if all parameters in params fit the data in a dict
    """
    def _filter_helper(item):
        """
        helper function that does an appropriate check
        for each element in params depending on the type:
            compare dates and ints with == operator
            and strings with in operator
        returns True iff all the elements in params match
        else False
        """
        for key, val in params.items():
            date = get_date(val)
            try:
                if date is not None:
                    if date != item[key]:
                        return False
                elif val.isdigit():
                    if int(val) != item[key]:
                        return False
                elif val.isalpha():
                    if val not in item[key]:
                        return False
            except TypeError:
                # inconsistent input(e.g. id=fi)
                return False
        return True

    return filter(_filter_helper, dict_list)


# API for teams
def get_driver_urls(team_id):
    """
    returns a list of urls for drivers for a given team
    """
    return [
        driver_repr(d['id'])['url'] for d in drivers
        if d['team'] == team_id
    ]


def get_driver_names(team_id):
    """
    returns a list of names for drivers for a given team
    """
    return [
        d['driver'] for d in drivers
        if d['team'] == team_id
    ]


def get_driver_ids(team_id):
    """
    returns a list of names for drivers for a given team
    """
    return [
        d['id'] for d in drivers
        if d['team'] == team_id
    ]


def team_repr(key):
    """
    json representation of a team
    """
    return {
        'url': request.host_url.rstrip('/') + url_for('team_detail', key=key),
        # subtract 1 to prevent index error when matching against id
        'data': teams[key-1],
        # 'drivers': get_driver_urls(key)
        'drivers': get_driver_names(key)
    }


@app.route("/teams/")
def team_list():
    """
    List teams filtered by search paramteres if applicable
    """
    params = {
        key: val for key, val in request.args.items()
        if key in TEAM_FILTER_FIELDS
    }
    return [team_repr(t['id']) for t in filter_by_params(teams, params)]


@app.route("/teams/<int:key>/")
def team_detail(key):
    """
    Retrieve team instances.
    """
    if key not in range(1, len(teams)+1):
        raise exceptions.NotFound()
    return team_repr(key)


# API for drivers
def driver_repr(key):
    """
    json representation of a driver
    """
    # subtract 1 to prevent list index error when matching against id
    driver_data = drivers[key-1]
    return {
        'url': request.host_url.rstrip('/') + url_for(
            'driver_detail', key=key
        ),
        'team_url': request.host_url.rstrip('/') + url_for(
            'team_detail', key=driver_data['team']
        ),
        'data': driver_data
    }


@app.route("/drivers/")
def driver_list():
    """
    List drivers filtered by search paramteres if applicable
    """
    params = {
        key: val for key, val in request.args.items()
        if key in DRIVER_FILTER_FIELDS
    }
    return [driver_repr(d['id']) for d in filter_by_params(drivers, params)]


@app.route("/drivers/<int:key>/")
def driver_detail(key):
    """
    Retrieve driver instances.
    """
    if key not in range(1, len(drivers)+1):
        raise exceptions.NotFound()
    return driver_repr(key)


# API for races
def race_repr(key, data=races):
    """
    json representation of a race
    """
    return {
        'url': request.host_url.rstrip('/') + url_for(
            'race_detail', key=key
        ),
        'data': data[key-1]
    }


@app.route("/races/", methods=['GET', 'POST'])
def race_list():
    """
    List races or create a new one
    """
    if request.method == 'POST':
        # race(name), date, and dict of drivers: number of points
        race_data = {
            'race': request.data.get('race'),
            'date': request.data.get('date'),
            'drivers': request.data.get('drivers')
        }
        # we got valid JSON, lets now validate the content
        # check if we have correct types for race_data values
        _types = {'race': basestring, 'date': basestring, 'drivers': dict}
        if not all(
                isinstance(race_data[key], _types[key]) for key in race_data):
            raise exceptions.ParseError(
                'Invalid data, race and date have to be string/unicode,'
                'drivers has to be a dict of the form id: score'
            )
        # parse date
        race_data['date'] = get_date(race_data['date'])
        if race_data['date'] is None:
            raise exceptions.ParseError(
                'Incorrect date format, should be YYYY-MM-DD'
            )
        # ok, the data seems right, lets validate the driver dict
        # make sure we have at least 1 driver
        if len(race_data['drivers']) < 1:
            raise exceptions.ParseError('Please specify at least 1 driver')
        # check if all drivers actually exists and their score is an int
        if not all(
                int(_id) in range(1, len(drivers)+1) and isinstance(score, int)
                for _id, score in race_data['drivers'].items()):
            raise exceptions.ParseError(
                'Unknown driver id or score is not an integer'
            )
        # finally add the instance to our races list
        races.append(race_data)
        return race_repr(len(races)), status.HTTP_201_CREATED
    # request.method == 'GET'
    # find params that we can immediately check
    default_params = {
        key: val for key, val in request.args.items()
        if key in RACE_FILTER_FIELDS
    }
    # filter races by name or/and date
    races_clean = filter_by_params(races, default_params)
    # return races sorted by date from latest to earliest
    return sorted(
        [race_repr(i, races_clean) for i in range(1, len(races_clean)+1)],
        key=lambda race: race['data']['date'],
        reverse=True
    )


@app.route("/races/<int:key>/")
def race_detail(key):
    """
    Retrieve race instance
    """
    if key not in range(1, len(races)+1):
        raise exceptions.NotFound()
    return race_repr(key)


# API for team and driver leaderboards
def _driver_standings_helper():
    """
    helper function to return list of
    driver standings sorted from best to worst.
    """
    # get tuples (driver_id, points) for all existing races
    driver_scores = [
        (_id, points) for r in races
        for _id, points in r['drivers'].items()
    ]
    # intialize all scores
    standings = {driver_id: 0 for driver_id, _ in driver_scores}
    # fill data in
    for _id, points in driver_scores:
        standings[_id] += points

    return standings.items()


def sort_and_enumerate(data, repr_function):
    """
    helper function that takes list of 2d tuples(driver/team, score)
    and a representation function, reverse sorts the list by 2nd element,
    returning an enumerated OrderedDict
    """
    # sort by scores descending
    data.sort(
        key=lambda (_, scores): scores,
        reverse=True
    )
    # add indices to mimic a leaderboard
    return OrderedDict(
        (i+1, ({'info': repr_function(int(_id)), 'score': score}))
        for i, (_id, score) in enumerate(data)
    )


@app.route("/driver_standings/")
def driver_standings():
    """
    Retrieve driver standings sorted from best to worst.
    """
    return sort_and_enumerate(_driver_standings_helper(), driver_repr)


@app.route("/team_standings/")
def team_standings():
    """
    Retrieve team standings sorted from best to worst.
    """
    all_drivers = dict(_driver_standings_helper())
    standings = {}
    for t in teams:
        # out of all drivers in the race find the ones
        # who belong to this team t
        drivers_in_race = filter(
            lambda d: d in all_drivers,
            map(str, get_driver_ids(t['id']))
        )
        # we have at least 1 such driver
        # explicit check for readability
        if drivers_in_race != []:
            # make entry team t: total score
            standings[t['id']] = sum(all_drivers[d] for d in drivers_in_race)

    return sort_and_enumerate(standings.items(), team_repr)


if __name__ == '__main__':
    app.run(debug=True)
