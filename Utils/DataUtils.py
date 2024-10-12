import numpy as np

import csv

import geopandas as gp

def load_clustering_data(
        names_path: str,
        gdp_path: str,
        population_path: str,
        currency_path: str,
        map_path: str,
        n: int,
        T_gdp: int,
        T_pop: int,
        T_currency: int
    ):
    """
    Loads all data required for clustering from .csv and .txt files

    Parameters:
        names_path (str): The path to the file containing each country's ISO3 code
        gdp_path (str): The path to the file containing each country's GDP data
        population_path (str): The path to the file containing each country's population data
        currency_path (str): The path to the file containing each country's currency exchange rate data
        map_path (str): The path to the map data
        n (int): The number of countries in the dataset
        T_gdp (int): The amount of years GDP data is available for (ending in 2017)
        T_pop (int): The amount of years population data is available for (ending in 2017)
        T_currency (int): The amount of years currency exchange rate data is available for (ending in 2017)

    Returns:
        list[str]: The list of ISO3 codes for each country in the dataset
        np.ndarray: The annual GDP per capita data for each country
        np.ndarray: The annual population data for each country
        np.ndarray: The annual bilateral exchange rate of each country's currency
        gd.GeoDataFrame: The map, used for visualization of clustering results
    """
    names = []
    with open(names_path, 'r') as file:
        rows = file.readlines()
        for row in rows:
            names.append(row[:3])

    gdp = np.zeros((n,T_gdp))
    with open(gdp_path, 'r') as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                gdp[j][i] = float(val)

    pop = np.zeros((n, T_pop))
    with open(population_path, 'r') as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                pop[j][i] = float(val)

    currency = np.zeros((n, T_currency))
    with open(currency_path, 'r') as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                currency[i][j] = float(val)

    world = gp.read_file(map_path)

    return names, gdp, pop, currency, world

def load_locations(
        n: int,
        locations_path: str    
    ) -> np.ndarray:
    """
    Loads the locations of the countries

    Parameters:
        n (int): The number of countries in the dataset
        locations_path (str): The path to the csv file containing the locations
    
    Returns:
        np.ndarray: The (longitude, latitude) matrix of all locations
    """
    locations = np.zeros((n,2))

    with open(locations_path, 'r') as file:
        rows = csv.reader(file)
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                locations[i][j] = val

    return locations

def load_groups(groups_path: str) -> list:
    """
    Loads the country groups used for post-processing

    Parameters:
        groups_path (str): The path to the .txt file containing group information
    
    Returns:
        list: The list of tuples (name, members), where name is a string and members is a list of ISO3 country codes
    """
    groups = []

    with open(groups_path, 'r') as file:
        rows = file.readlines()
        row_no = 0
        while row_no < len(rows)-1:
            groups.append((rows[row_no][:-1], rows[row_no+1][:-1].split(',')))
            row_no += 2
        
    return groups

def load_forecast_data(
        names_path: str,
        gdp_path: str,
        n: int,
        T_gdp: int,
    ):
    """
    Loads all data required for neural network regression from .csv and .txt files

    Parameters:
        names_path (str): The path to the file containing each country's ISO3 code
        gdp_path (str): The path to the file containing each country's GDP data
        n (int): The number of countries in the dataset
        T_gdp (int): The amount of years GDP data is available for (ending in 2017)

    Returns:
        list[str]: The list of ISO3 codes for each country in the dataset
        np.ndarray: The annual GDP per capita data for each country
    """
    names = []
    with open(names_path, 'r') as file:
        rows = file.readlines()
        for row in rows:
            names.append(row[:3])

    gdp = np.zeros((n,T_gdp))
    with open(gdp_path, 'r') as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                gdp[j][i] = float(val)

    return names, gdp