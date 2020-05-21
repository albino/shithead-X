import configparser
import json

initial_data = {
    "ignore_list": [],
}

def config(path):
    ret = configparser.ConfigParser()
    ret.read(path)
    return ret

def read_data(path):
    try:
        with open(path) as data_file:
            data = json.load(data_file)
            if data:
                return data
            else:
                return initial_data
    except:
        return initial_data

def save_data(path, data):
    with open(path, 'w') as data_file:
        json.dump(data, data_file)
