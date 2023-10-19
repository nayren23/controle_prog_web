#!/usr/bin/python
from configparser import ConfigParser
import getpass
PASSWORD = getpass.getpass()
def config(filename='config.ini', section='postgresql'):
    parser = ConfigParser() # create a parser
    parser.read(filename) # read config file
    db = {} # get section, default to postgresql
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            if param[0] == "password":
                db[param[0]] = PASSWORD
            else:
                db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db