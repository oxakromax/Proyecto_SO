import pandas as pd

"""Define the paths of data"""
path_manana = "C:\\Users\\oxakr\\PycharmProjects\\Proyecto SO\\data\\manana.dat"
path_noche = "C:\\Users\\oxakr\\PycharmProjects\\Proyecto SO\\data\\noche.dat"
path_tarde = "C:\\Users\\oxakr\\PycharmProjects\\Proyecto SO\\data\\tarde.dat"
path_request_1 = "C:\\Users\\oxakr\\PycharmProjects\\Proyecto SO\\data\\requests_1.dat"
path_request_2 = "C:\\Users\\oxakr\\PycharmProjects\\Proyecto SO\\data\\requests_2.dat"
path_request_3 = "C:\\Users\\oxakr\\PycharmProjects\\Proyecto SO\\data\\requests_3.dat"

"""Read data"""

data_parsing_manana = pd.read_csv(path_manana, header=None, sep=' ')
data_parsing_noche = pd.read_csv(path_noche, header=None, sep=' ')
data_parsing_tarde = pd.read_csv(path_tarde, header=None, sep=' ')
data_parsing_request_1 = pd.read_csv(path_request_1, header=None, sep=' ')
data_parsing_request_2 = pd.read_csv(path_request_2, header=None, sep=' ')
data_parsing_request_3 = pd.read_csv(path_request_3, header=None, sep=' ')
