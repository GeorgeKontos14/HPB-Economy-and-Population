from re import M
import numpy as np

import pandas as pd

import geopandas as gp

import matplotlib.pyplot as plt

import networkx as nx

from SCC_Replication.Variables.State import H

def show_multiple_countries(
        codes: list[str],
        names: list[str],
        df: pd.DataFrame,
        start_year: int,
        duration: int    
    ):
    """
    Plots the different time series for multiple countries

    Parameters:
        codes (list[str]): The ISO3 country codes of the selected countries
        names (list[str]): The names of the selected countries
        df (pd.DataFrame): The full dataset
        start_year (int): The first year of the observations
        duration (int): The number of observations for each time series
    """
    selected_data = [df.loc[code].to_list() for code in codes]
    selected_gdp = [country[:duration] for country in selected_data]
    selected_pop = [country[duration:2*duration] for country in selected_data]
    selected_cur = [country[2*duration:] for country in selected_data]

    countries_str = ', '.join(names)

    plt.figure(figsize=(20,5))
    plt.title(f"GDP for {countries_str}")
    for i, row in enumerate(selected_gdp):
        plt.plot(range(start_year, start_year+duration), row, label=names[i])
    plt.xlabel('Year')
    plt.ylabel('GDP')
    plt.show()

    plt.figure(figsize=(20,5))
    plt.title(f"Population for {countries_str}")
    for i, row in enumerate(selected_pop):
        plt.plot(range(start_year, start_year+duration), row, label=names[i])
    plt.xlabel('Year')
    plt.ylabel('Population')
    plt.show()

    plt.figure(figsize=(20,5))
    plt.title(f"Currency for {countries_str}")
    for i, row in enumerate(selected_cur):
        plt.plot(range(start_year, start_year+duration), row, label=names[i])
    plt.xlabel('Year')
    plt.ylabel('Currency')

def plot_clusters(
        k: int,
        data: np.ndarray,
        cluster_centers: np.ndarray,
        labels: np.ndarray,
        rows: int,
        columns: int,
        start_year: int,
        T: int,
        title: str = None
    ):
    """
    Plots the clusters and their centroids in separate subplots

    Parameters:
        k (int): The number of clusters
        data (np.ndarray): The dataset that has been clustered
        cluster_centers (np.ndarray): The centroids of the clusters
        labels (np.ndarray): The labels that the clustering algorithm assigns to the data
        rows (int): The number of rows of subplots
        columns (int): The number of columns of subplots 
        start_year (int): The first year of observations
        T (int): The duration of the time series
        title (str): The title to be used in the graph
    """
    time = np.arange(start_year, start_year+T)
    plt.figure(figsize=(20, 10))
    if title is not None:
        plt.suptitle(title)
    for yi in range(k):
        plt.subplot(rows, columns, yi+1)
        for xx in data[labels == yi]:
            plt.plot(time, xx.ravel(), alpha=.7)
        if cluster_centers is not None:
            plt.plot(time, cluster_centers[yi].ravel(), 'lime')
        plt.text(0.55, 0.85, f'Cluster {yi+1}',
                transform=plt.gca().transAxes)

def show_clustering(
        countries: list[str],
        k: int,
        data: np.ndarray,
        cluster_centers: np.ndarray,
        labels: np.ndarray,
        score: float,
        rows: int,
        columns: int,
        start_year: int,
        T: int,
        title: str = None
    ) -> list[list[str]]:
    """
    Displays all relevant information for a clustering algorithm instance, including the visualization of the clusters, the silhouette score, and which countries are assigned to each cluster

    Parameters:
        countries (list[str]): The ISO3 country codes of all the clustered countries
        k (int): The number of clusters
        data (np.ndarray): The dataset that has been clustered
        cluster_centers (np.ndarray): The centroids of the clusters
        labels (np.ndarray): The labels that the clustering algorithm assigns to the data
        score (float): The silhouette score of the clustering
        rows (int): The number of rows of subplots
        columns (int): The number of columns of subplots
        start_year (int): The first year of observations
        T (int): The duration of the time series
        title (str): The title to be used in the graph
    
    Returns:
        list[list[str]]: The list containing the country names per cluster
    """
    plot_clusters(k, data, cluster_centers, labels, rows, columns, start_year, T, title)

    clusters = summarize_clustering(countries, k, labels, score)
    
    return clusters

def summarize_clustering(
        countries: list[str],
        k: int,
        labels: np.ndarray,
        score: float
    ) -> list[list[str]]:
    """
    Presents a summary of the clustering results

    Parameters:
        countries (list[str]): The ISO3 country codes of all the clustered countries
        k (int): The number of clusters
        labels (np.ndarray): The labels that the clustering algorithm assigns to the data
        score (float): The silhouette score of the clustering
    
    Returns:
        list[list[str]]: The list containing the country names per cluster
    """
    print(f"Silhouette Score: {score}")

    clusters = [[] for _ in range(k)]
    for i in range(k):
        members = np.where(labels == i)[0]
        for member in members:
            clusters[i].append(countries[member])
        print(f"Cluster #{i+1} size: {len(clusters[i])}")
        print(f"Cluster #{i+1} members: {', '.join(clusters[i])}")
    
    return clusters

def plot_centroids_outliers(
        cluster_centers: np.ndarray,
        outliers: np.ndarray,
        start_year: int,
        T: int,
        title: str = None
    ):
    """
    Plots the cluster centers and outliers on the same graph. The outliers are plotted in red and the cluster centers are plotted in green

    Parameters:
        cluster_centers (np.ndarray): The centroids determined by the clustering algorithm
        outliers (np.ndarray): The outlier data, eliminated from the clustered dataset
        start_year (int): The first year of observations
        T (int): The duration of the time series
        title (str): The title to be used in the graph
    """
    time = np.arange(start_year, start_year+T)

    plt.figure(figsize=(20,5))
    if title is not None:
        plt.suptitle(title)
    
    for center in cluster_centers:
        plt.plot(time, center.ravel(), 'lime')
    
    for outlier in outliers:
        plt.plot(time, outlier.ravel(), 'red')

    centers_line = plt.Line2D([0],[0], color='lime', lw=2)
    outliers_line = plt.Line2D([0], [0], color='red', lw=2)

    plt.legend([centers_line, outliers_line], ['Centroids', 'Outliers'])

def show_clusters_on_map(
        countries: list[str],
        labels: np.ndarray,
        world: gp.GeoDataFrame,
        title: str = None  
    ):
    """
    Visualizes the clustering results on a world map

    Parameters:
        countries (list[str]): The ISO3 country codes of all the clustered countries for all countries in the dataset
        labels (np.ndarray): The labels that the clustering algorithm assigns to the data
        world (gp.GeoDataFrame): The dataframe containing map information
        title (str): The title to be used in the graph
    """
    y_frame = pd.DataFrame({
        'CODE': countries,
        'LABEL': labels
    })

    df = world.merge(y_frame, how='inner', left_on='ISO_A3_EH', right_on='CODE')

    fig, ax = plt.subplots(1,1, figsize=(15,10))
    fig.patch.set_facecolor('white')
    if title is not None:
        plt.title(title, color='black')
    
    df.plot(column='LABEL', ax=ax)
    ax.axis('off')

    plt.tight_layout()
    plt.show()

def plot_group_graph(
        members: list[str], 
        edges: list, 
        edge_colors: list[str], 
        edge_thickness: list[float], 
        title: str = None
    ):
    """
    Plots the grap for a group of countries

    Parameters:
        members (list[str]): the list of countries in the group
        edges (list): The list of the edges as tuples (u, v, w), where u and v are the nodes and w is the weight of the edge
        edge_colors (list[str]): The list of colors of the edges
        edge_thickness (list[float]): The list of thickness of the edges
        title (str): The title to be used in the graph
    """
    G = nx.Graph()
    G.add_nodes_from(members)
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=round(edge[2], 3))
    
    plt.figure(figsize=(12,12))
    if title is not None:
        plt.title(title)
    
    pos = nx.spring_layout(G)
    nx.draw(
        G, 
        pos, 
        with_labels=True, 
        node_color='gold', 
        width=edge_thickness,
        node_size=800,
        edge_color=edge_colors    
    )
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.tight_layout()
    plt.show()

def plot_arima_orders(arima_orders: np.ndarray):
    """
    Plots a summary of the ARIMA orders for multiple time series

    Parameters:
        arima_orders (np.ndarray): The (n,3) array (n: # time series), where each row is the (p,d,q) ARIMA orders
    """

    unique_values = np.unique(arima_orders)

    cols = ['Autoregression Order', 'Differentiation Order', 'Moving Average Order']
    colors = ['orange', 'purple', 'teal']

    counts = {value: [np.sum(arima_orders[:, col] == value) for col in range(
        arima_orders.shape[1])] for value in unique_values}

    x = np.arange(len(unique_values))
    bar_width = 0.25

    for i in range(arima_orders.shape[1]):
        counts_per_column = [counts[value][i] for value in unique_values]
        plt.bar(x + i * bar_width, counts_per_column, 
            width=bar_width, label=cols[i], color=colors[i])
    
    plt.xticks(x + bar_width * (arima_orders.shape[1] - 1) / 2, unique_values)
    plt.xlabel("Values")
    plt.ylabel("Frequency")
    plt.title("Frequency of Values")
    plt.legend()
    plt.show()

def plot_forecast_intervals(
        data_train: pd.Series,
        data_test: pd.Series,
        country: str,
        in_sample: pd.DataFrame = None,
        test_preds: pd.DataFrame = None,
        horizon_preds: pd.DataFrame = None,
        ax = None,
        title: str = None,
        show_legend: bool = True,
        show67: bool = True,
        show90: bool = True
    ):
    """
    Plots the probabilistic forecast for a given country

    Parameters:
        data_train (pd.Series): The training part of the GDP time series
        data_test (pd.Series): The testing_part of the GDP time series
        country (str): The name of the country
        in_sample (pd.DataFrame): The in-sample predictions for the time series
        test_preds (pd.DataFrame): The predictions for the test set
        horizon_preds (pd.DataFrame): The future predictions
        ax: The object to be used for plotting
        title (str): The title of the plot; if none, the name of the country
        show_legend (bool): Whether or not to display a legend alongside the plot. 
        show67 (bool): Flag indicating whether or not to plot the 67% prediction intervals
        show90 (bool): Flag indicating whether or not to plot the 90% prediction intervals           
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))

    if title is None:
        ax.set_title(country)
    else:
        ax.set_title(title)

    data_train.plot(ax=ax, label='Train', color='black')
    data_test.plot(ax=ax, label="Test", color='green')

    if in_sample is not None:
        if show67:
            ax.fill_between(
                in_sample.index,
                in_sample[f'{country}_q_0.16'],
                in_sample[f'{country}_q_0.84'],
                color = 'lightskyblue',
                alpha=0.8,
                label = f'67% interval (in-sample)'
            )
        if show90:
            ax.fill_between(
                in_sample.index,
                in_sample[f'{country}_q_0.05'],
                in_sample[f'{country}_q_0.95'],
                color = 'lightskyblue',
                alpha=0.3,
                label = f'90% interval (in-sample)'
            )

    if test_preds is not None:
        if show67:
            ax.fill_between(
                test_preds.index,
                test_preds[f'{country}_q_0.16'],
                test_preds[f'{country}_q_0.84'],
                color = 'orange',
                alpha=0.8,
                label = f'67% interval (test)'
            )
        if show90:
            ax.fill_between(
                test_preds.index,
                test_preds[f'{country}_q_0.05'],
                test_preds[f'{country}_q_0.95'],
                color = 'orange',
                alpha=0.3,
                label = f'90% interval (test)'
            )
    if horizon_preds is not None:
        horizon_preds[f'{country}_q_0.5'].plot(ax=ax, color='red', label = 'Median (horizon)')
        horizon_preds[f'{country}_mean'].plot(ax=ax, color='blueviolet', label='Mean (horizon)')
        if show67:
            ax.fill_between(
                horizon_preds.index,
                horizon_preds[f'{country}_q_0.16'],
                horizon_preds[f'{country}_q_0.84'],
                color = 'coral',
                alpha=0.8,
                label = f'67% interval (horizon)'
            )
        if show90:
            ax.fill_between(
                horizon_preds.index,
                horizon_preds[f'{country}_q_0.05'],
                horizon_preds[f'{country}_q_0.95'],
                color = 'coral',
                alpha=0.3,
                label = f'90% interval (horizon)'
            )

    if show_legend:
        ax.legend()  

def plot_many_predictions(
        data_train: pd.DataFrame,
        data_test: pd.DataFrame,
        country: str,
        titles: list[str],
        rows: int,
        columns: int,
        in_sample_preds: list[pd.DataFrame] = None,
        test_preds: list[pd.DataFrame] = None,
        horizon_preds: list[pd.DataFrame] = None,
        show67: bool = True,
        show90: bool = True,
        title: str = None
    ):
    """
    Plot multiple predictions for the same country

    Parameters:
        data_train (pd.Series): The training part of the GDP time series
        data_test (pd.Series): The testing_part of the GDP time series
        country (str): The name of the country    
        titles (list[str]): The titles of each of the subplots
        rows (int): The number of rows of plots
        columns (int): The number of columns of plots
        in_sample (list[pd.DataFrame]): The in-sample predictions for the time series
        test_preds (list[pd.DataFrame]): The predictions for the test set
        horizon_preds (list[pd.DataFrame]): The future predictions
        show67 (bool): Flag indicating whether or not to plot the 67% prediction intervals
        show90 (bool): Flag indicating whether or not to plot the 90% prediction intervals  
        title (str): The title of the plot; if none, the name of the country        
    """
    fig, axs = plt.subplots(rows, columns, figsize=(12,8))

    ax_list = axs.flatten()
    for i, ax in enumerate(ax_list):
        if in_sample_preds is not None:
            in_sample = in_sample_preds[i]
        else:
            in_sample = None
        if test_preds is not None:
            test = test_preds[i]
        else:
            test = None
        if horizon_preds is not None:
            horizon = horizon_preds[i]
        else:
            horizon = None

        plot_forecast_intervals(
            data_train, 
            data_test, 
            country, 
            in_sample=in_sample, 
            test_preds=test, 
            horizon_preds=horizon,
            ax=ax,
            title=titles[i],
            show_legend=False,
            show67=show67, 
            show90=show90
        )

    handles, labels = [], []
    ax = ax_list[0]
    for handle, label in zip(*ax.get_legend_handles_labels()):
        handles.append(handle)
        labels.append(label)

    fig.legend(handles, labels, loc='lower center', ncol=6, fontsize=10)

    if title is None:
        fig.suptitle(country, fontsize=16)
    else:
        fig.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0,0.05,1,0.92])
    plt.show()

def plot_prediction_and_baseline(
        country: str,
        model_type: str,
        ind: int,
        start_year: int,
        T: int,
        gdp: np.ndarray,
        low_freq: np.ndarray,
        horizon_preds: pd.DataFrame,
        q05: np.ndarray,
        q16: np.ndarray,
        q84: np.ndarray,
        q95: np.ndarray,
        title: str = None
    ):
    """
    Plot the prediction intervals of a specific model and the baseline on the same plot

    Parameters:
        country (str): The name of the country
        model_type (str): The type of model that was used for the predictions
        ind (int): The index corresponding to the country
        start_year (int): The start year of the observed data
        T (int): The duration of the observed data
        gdp (np.ndarray): The observed GDP data for all countries
        low_freq (np.ndarray): The low-frequency trend of the observed data
        horizon_preds (pd.Dataframe): The future predictions
        q05 (np.ndarray): The 5th baseline quantile
        q16 (np.ndarray): The 16th baseline quantile
        q84 (np.ndarray): The 84th baseline quantile
        q95 (np.ndarray): The 95th baseline quantile
        title (str): The title of the plot; if none, the name of the country  
    """
    T_horizon = len(q05[:,0])
    in_sample_time = np.arange(start_year, start_year+T)
    horizon_time = np.arange(start_year+T, start_year+T+T_horizon)

    fig, axs = plt.subplots(2, 1, figsize=(14,10))
    ax_list = axs.flatten()

    ax = ax_list[0]
    ax.plot(in_sample_time, gdp[ind], color='black', label='Observed Values')
    ax.plot(in_sample_time, low_freq[:,ind], color='deepskyblue', alpha=0.75, label='Low Frequency Trend')
    ax.fill_between(
        horizon_time, q16[:, ind], q84[:, ind], color='lightskyblue', alpha=0.5, label='Baseline Prediction Interval'
    )
    ax.fill_between(
        horizon_time, horizon_preds[f'{country}_q_0.16'], horizon_preds[f'{country}_q_0.84'], color='coral', alpha=0.5, label=f'{model_type} Prediction Interval'
    )
    ax.set_title(f'67% Prediction Intervals')

    ax = ax_list[1]
    ax.plot(in_sample_time, gdp[ind], color='black', label='Observed Values')
    ax.plot(in_sample_time, low_freq[:, ind], color='deepskyblue', alpha=0.75, label='Low Frequency Trend')
    ax.fill_between(
        horizon_time, q05[:, ind], q95[:, ind], color='lightskyblue', alpha=0.5, label='Baseline Prediction Interval'
    )
    ax.fill_between(
        horizon_time,  horizon_preds[f'{country}_q_0.05'], horizon_preds[f'{country}_q_0.95'], color='coral', alpha=0.5, label=f'{model_type} Prediction Interval'
    )
    ax.set_title(f'90% Prediction Intervals')

    handles, labels = [], []
    for handle, label in zip(*ax.get_legend_handles_labels()):
        handles.append(handle)
        labels.append(label)
    
    fig.legend(handles, labels, loc='lower center', ncol=6, fontsize=10)
    if title is None:
        fig.suptitle(country, fontsize=16)
    else:
        fig.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0,0.05,1,0.92])
    plt.show()
