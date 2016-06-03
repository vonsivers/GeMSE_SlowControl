#! /usr/bin/env python3.3

"""
Little script that provides you with the data from the Doberman slow control DB. For example to make more complex plots than with the online monitior.
"""

import datetime
import DobermanDB
import logging
from argparse import ArgumentParser
import json

logging.basicConfig()
DobermanDBconnection = None

def prepare_DB_connection():
    """
    set up the connection to the DB
    """
    parser = ArgumentParser()
    opts = parser.parse_args()
    logger = logging.getLogger()
    DDB = DobermanDB.DobermanDB(opts, logger)
    return sDB

DobermanDBconnection = prepare_DB_connection()

def json_date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def isotime2datetime(isotime):
    return datetime.datetime.strptime(isotime, "%Y-%m-%dT%H:%M:%S")

def fetch_data_controller(name, datetimestamp = None, limit = 100):
    """
    Get the data of a controller
    """
    data = DobermanDBconnection.getData(name, limit, datetimestamp)
    return data

def _dump_data_2file(data, datafilename):
    """
    Dump data set to file
    """
    with open(datafilename, 'w') as dfile:
        json.dump(data, dfile, default=json_date_handler)
    return 1

def _read_datafile(datafilename):
    """
    read the data set of an controller again
    """
    with open(datafilename, 'r') as dfile:
        data = json.load(dfile)
    return data

def slowDB2file(name, datetimestamp = None, limit = 100):
    """
    read data of controller from db and write to a file
    """
    data = fetch_data_controller(name, datetimestamp, limit)
    datafilename = "slowcontrolDBdata_%s.dat"%name
    _dump_data_2file([name, DobermanDBconnection.readConfig(name), datetimestamp, data], datafilename)
    return 1

def slowDB2dict(name, datetimestamp = None, limit = 100):
    """
    read data of controller from db to dict
    """
    data = fetch_data_controller(name, datetimestamp, limit)

def jsonfile2dict(datafilename):
    """
    read data from json file and stuff it into an dict
    """
    data = _read_datafile(datafilename)
    dic = dict(zip(['name','config','datetimeselector','data'],data))
    dic['config'] = dict(zip(DobermanDBconnection.getConfigColumnNames(),dic['config'][-1]))
    return dic
