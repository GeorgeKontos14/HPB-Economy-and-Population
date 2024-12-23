from typing import Tuple, Union

import numpy as np

import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import KNNImputer

from tslearn.preprocessing import TimeSeriesScalerMeanVariance

def fill_data(arr: np.ndarray, neighbors: int = 3) -> np.ndarray:
    """
    Fills empty values in the input array using a KNN Imputer

    Parameters:
        arr (np.ndarray): The array to be filled
        neighbors (int): The number of neighbors for the KNN algorithm

    Returns:
        np.ndarray: The filled array
    """
    imputer = KNNImputer(n_neighbors=neighbors)
    return imputer.fit_transform(arr)

def pca(data: np.ndarray, variance: float = 0.95) -> np.ndarray:
    """
    Performs Principal Component Analysis on the input data

    Parameters:
        data (np.ndarray): The initial dataset
        variance (float): The variance % of the dataset to be maintained. Based on this number, the PCA algorithm determines the number of principal components

    Returns:
        np.ndarray: The principal components of the input data
    """
    filled = data
    if np.sum(np.isnan(data)) > 0:
        filled = fill_data(data)
    return PCA(n_components=variance).fit_transform(filled)

def preprocess_pca(
        countries: list[str],
        gdp: np.ndarray, 
        pop: np.ndarray, 
        currency: np.ndarray, 
        variance: float=0.95
    ):
    """
    Constructs the final dataset to be used for the hierarchical clustering algorithms

    Parameters:
        countries (list[str]): The ISO3 code for each country (to be used as indices)
        gdp (np.ndarray): The matrix containing the annual GDP per capita for each country
        pop (np.ndarray): The matrix containing the annual population of each country
        currency (np.ndarray): The matrix containing the annual bilateral exchange rate of each country's currency and the US Dollar
        variance (float): The variance % of the dataset to be maintained. Based on this number, the PCA algorithm determines the number of principal components

    Returns:
        pd.DataFrame: The dataset where each country is represented by the concatenation of the principal components of its three time series (gdp, population and currency exchange rate)
        pd.DataFrame: The scaled version of the dataset
    """
    df = pd.DataFrame({})
    scaler = StandardScaler()
    
    gdp_components = pca(gdp, variance)
    for i in range(gdp_components.shape[1]):
        df[f"GDP #{i}"] = gdp_components[:,i]
    
    pop_components = pca(pop, variance)
    for i in range(pop_components.shape[1]):
        df[f"Population #{i}"] = pop_components[:,i]
    
    currency_components = pca(currency, variance)
    for i in range(currency_components.shape[1]):
        df[f"Currency #{i}"] = currency_components[:,i]
    
    df.index = countries
    scaled_data = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns, index=df.index)
    return df, scaled_df

def preprocess(        
        countries: list[str],
        gdp: np.ndarray, 
        pop: np.ndarray, 
        currency: np.ndarray,
        start_year: int
    ):
    """
    Constructs the final dataset to be used for the spectral clustering algorithm

    Parameters:
        countries (list[str]): The ISO3 code for each country (to be used as indices)
        gdp (np.ndarray): The matrix containing the annual GDP per capita for each country
        pop (np.ndarray): The matrix containing the annual population of each country
        currency (np.ndarray): The matrix containing the annual bilateral exchange rate of each country's currency and the US Dollar
        start_year (int): The start year of the data

    Returns:
        pd.DataFrame: The dataset where each country is represented by the concatenation of the three time series (gdp, population and currency exchange rate)
        pd.DataFrame: The scaled version of the dataset
    """
    scaler = StandardScaler()
    gdp_columns = {f"GDP {i+start_year}": gdp[:,i] for i in range(gdp.shape[1])}
    gdp_df = pd.DataFrame(gdp_columns)

    pop_columns = {f"Population {i+start_year}": pop[:, i] for i in range(pop.shape[1])}
    pop_df = pd.DataFrame(pop_columns)

    currency_data = fill_data(currency)
    currency_columns = {f"Currency {i+start_year}": currency_data[:, i] for i in range(currency_data.shape[1])}
    currency_df = pd.DataFrame(currency_columns)

    df = pd.concat([gdp_df, pop_df, currency_df], axis=1)
    df.index = countries
    scaled_data = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns, index=df.index)

    return df, scaled_df

def preprocess_onlyGDP(
        countries: list[str],
        gdp: np.ndarray, 
        start_year: int,
        T: int,
        zero_mean: bool = True
    ):
    """
    Constructs the final dataset to be used for the clustering algorithm only considering the GDP per capita time series

    Parameters:
        countries (list[str]): The ISO3 code for each country (to be used as indices)
        gdp (np.ndarray): The matrix containing the annual GDP per capita for each country
        start_year (int): The start year of the data
        T (int): The amount of years for which data is collected
        zero_mean (bool): Whether or not to change the time series mean to zero

    Returns:
        pd.DataFrame: The dataset
        pd.DataFrame: The scaled version of the dataset
        np.ndarray: The scaled version of the dataset in a numpy array
    """
    scaler = TimeSeriesScalerMeanVariance()
    df = pd.DataFrame({start_year+i: gdp[:, i] for i in range(T)})
    df.index = countries
    scaled_data = np.squeeze(scaler.fit_transform(df))
    if not zero_mean:
        scaled_data += np.mean(gdp, axis=1)[:, np.newaxis]
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns, index=df.index)

    return df, scaled_df, scaled_data


def make_indexes(
        start_year: int,
        split_ind: int,
        T: int
    ) -> Tuple[pd.DatetimeIndex, pd.DatetimeIndex, pd.DatetimeIndex]:
    """
    Creates datetime indices for the specified period

    Parameters:
        start_year (int): The start year of the time series
        split_ind (int): The index where the training and test sets are split
        T (int): The length of the time series

    Returns:
        pd.DatetimeIndex: The index of the training set
        pd.DatetimeIndex: The index of the test set
        pd.DatetimeIndex: The index of the entire dataset
    """
    T_train = pd.date_range(start=f'{start_year}', end=f'{start_year+split_ind}', freq='Y')
    T_test = pd.date_range(start=f'{start_year+split_ind}', end=f'{start_year+T}', freq='Y')
    T_all = pd.date_range(start=f'{start_year}', end=f'{start_year+T}', freq='Y')

    return T_train, T_test, T_all

def preprocess_univariate_forecast(
        y: np.ndarray,
        start_year: int,
        train_split: float
    ) -> Tuple[int, pd.Series, pd.Series, pd.Series]:
    """
    Creates a training and a test set for a given dataset.

    Parameters:
        y (np.ndarray): The dataset
        start_year (int): The start year of the time series
        train_split (float): The split between train and test set (must be in (0,1))
    
    Returns:
        int: The number of test steps
        pd.Series: The training set
        pd.Series: The test set
        pd.Series: The dataset in a Series form
    """

    T = len(y)
    split_ind = int(train_split*T)
    test_steps = T-split_ind

    T_train, T_test, T_all = make_indexes(
        start_year=start_year, split_ind=split_ind, T=T
    )

    data_train = pd.Series(y[:split_ind], index=T_train)
    data_test = pd.Series(y[split_ind:], index=T_test)
    data_all = pd.Series(y, index=T_all)

    return test_steps, data_train, data_test, data_all   

def preprocess_multivariate_forecast(
        countries: list[str],
        y: np.ndarray,
        start_year: int,
        train_split: float
    ) -> Tuple[int, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Creates a training and a test set for a given dataset.

    Parameters:
        countries (list[str]): The countries in the dataset
        y (np.ndarray): The dataset
        start_year (int): The start year of the time series
        train_split (float): The split between train and test set (must be in (0,1))
    
    Returns:
        int: The number of test steps
        pd.DataFrame: The training set
        pd.DataFrame: The test set
        pd.DataFrame: The dataset in a dataframe form
    """
    T = y.shape[1]
    split_ind = int(T*train_split)
    test_steps = T-split_ind

    T_train, T_test, T_all = make_indexes(
        start_year=start_year, split_ind=split_ind, T=T
    )

    data_train = pd.DataFrame(y[:, :split_ind].T, index=T_train, columns=countries)
    data_test = pd.DataFrame(y[:, split_ind:].T, index=T_test, columns=countries)
    data_all = pd.DataFrame(y.T, index=T_all, columns=countries) 

    return test_steps, data_train, data_test, data_all