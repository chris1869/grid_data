#Created with codemiums
from selenium import webdriver
import pandas as pd
import hashlib
import os
import json
import time
import pycountry
def create_checksum(url):
    """
    Calculate the SHA-256 checksum of the given URL.

    Args:
        url (str): The URL to calculate the checksum for.

    Returns:
        str: The SHA-256 checksum of the URL.
    """
    checksum = hashlib.sha256(url.encode()).hexdigest()
    return checksum

def create_energy_url(year=2024, source="public"):
    """
    Creates an URL pointing to the relevant subsection of energy-charts.info based on the provided year and source.

    Args:
        year (int): The year for which the energy data is requested. Defaults to 2024.
        source (str): The data source for the energy data. Defaults to "public".

    Returns:
        str: The constructed energy URL.
    """
    base_url = "https://www.energy-charts.info/charts/power/chart.htm?l=en"
    return base_url + f"&c=DE&source={source}&interval=year&year={year}"

def create_capacity_url():
    """
    Creates a URL for the installed power capacity data.

    Returns:
        str: The URL for the installed power capacity data.
    """
    return "https://www.energy-charts.info/charts/installed_power/chart.htm?l=en&c=DE&year=-1"

def create_trading_country_url(country_code, year):
    """
    Creates a URL for trading data of a specific country and year.

    Args:
        country_code (str): The country code ISO alpha-2 code of the country for which the trading data is requested.
        year (int): The year for which the trading data is requested.

    Returns:
        str: The URL for trading data of the specified country and year.
    """
    base_url = "https://www.energy-charts.info/charts/power/chart.htm?l=en"
    return base_url + f"&c={country_code}&source=public&interval=year&year={year}"

def crawl_power_dataframe(driver_options, url):
    """
    Retrieves an energy dataframe from the given URL using the provided WebDriver.
    
    Args:
        driver_options (dict): The options for the WebDriver.
        url (str): The URL of the energy chart.
        
    Returns:
        pandas.DataFrame: The energy dataframe retrieved from the URL.
        
    Raises:
        None
    
    This function first creates a checksum of the URL to generate a cache filename. If the cache file does not exist,
    it opens the URL using the WebDriver, executes JavaScript to retrieve the series values from the Highcharts chart,
    and saves the JSON data to the cache file. Finally, it reads the JSON data from the cache file and returns the
    resulting pandas DataFrame.
    """
    print("Reading: ", url)
    check_sum = create_checksum(url)
    cache_fname = f"cache/{check_sum}.json"
    if not os.path.exists(cache_fname):
        # Initialize the webdriver
        driver = webdriver.Chrome(options=driver_options)
    #    Close the webdriver
        driver.get(url)
        time.sleep(5)
        script = """series_vals = {};
                    Highcharts.charts[0].series.forEach(function(s){series_vals[s.name] = [];s.data.forEach(function(d) {series_vals[s.name].push(d.y)});});
                    return series_vals;"""
        # Execute JavaScript to return JSON
        json_data = driver.execute_script(script)
        driver.quit()
        with open(cache_fname, "w") as f:
            json.dump(json_data, f)

    return pd.read_json(cache_fname)

def harmonize_columns(df, source):
    """
    Harmonizes columns in the DataFrame based on the data source (e.g., ensures naming is valid across all years, fusing columns,
    removing trading columns, etc.).
    
    Parameters:
    - df: DataFrame to harmonize columns
    - source: Data source type (e.g., "public", "public_trade", "entsoe", "total", "sw", "tcs_saldo")
    
    Returns:
    - DataFrame with harmonized columns based on the specified data source
    """
    if (source in ["public", "public_trade"]):
        if source == "public_trade":
            drop_cols = []
        else:
            df["Load"] = df.Load.fillna(0) + df["sum"].fillna(0) #Sum references Load pre 2015
            drop_cols = ["sum"]
        drop_cols.extend([col for col in df.columns if "share" in col]) # Remove share of load/generation columns
        drop_cols.extend([col for col in df.columns if "Auction" in col or "trading" in col]) # Remove auction/trading related columns
        df = df.drop(columns=drop_cols)
  
        hydro_cols = ["Pumped Storage", "Seasonal Storage"]
        hydro_cols.extend([col for col in df.columns if "Hydro" in col])
        
        df["Hydro"] = df[hydro_cols].fillna(0).sum(axis=1)
        df = df.drop(columns=hydro_cols)

        df["Nuclear"] = df["Nuclear"].fillna(0) + df["Uranium"].fillna(0)
        df.drop(columns=["Uranium"], inplace=True)

        df["Fossil gas"] = df["Fossil gas"].fillna(0) + df["Gas"].fillna(0) + df["Fossil coal-derived gas"].fillna(0)
        df.drop(columns=["Gas", "Fossil coal-derived gas"], inplace=True)

        df["Fossil brown coal / lignite"] = df["Fossil brown coal / lignite"].fillna(0) + df['Brown Coal'].fillna(0)
        df.drop(columns=["Brown Coal"], inplace=True)

        df["Fossil hard coal"] = df["Fossil hard coal"].fillna(0) + df["Hard Coal"].fillna(0)
        df.drop(columns=["Hard Coal"], inplace=True)

        df["Fossil oil"] = df["Fossil oil"].fillna(0) + df["Oil"].fillna(0)
        df.drop(columns=["Oil"], inplace=True)

        df["Wind onshore"] = df["Wind onshore"].fillna(0) + df["Wind"].fillna(0) # Wind before 2014 mostly from onshore
        df.drop(columns=["Wind"], inplace=True)

        if df.loc["2014"].shape != 0:
            #Reconstruct residual load
            renew_cols = set(df.columns).intersection(["Hydro", "Waste", "Wind offshore", "Wind onshore", "Solar", "Geothermal"])
            df.loc[:"2014", "Residual load"] = df.loc[:"2014", "Load"] - df.loc[:"2014", list(renew_cols)].sum(axis=1)
        return df

    if (source in ["entsoe", "total"]):
        print(df.columns)
        drop_cols = []
        drop_cols.extend([col for col in df.columns if "share" in col]) # Remove share of load/generation columns
        drop_cols.extend([col for col in df.columns if "Auction" in col or "trading" in col]) # Remove auction/trading related columns
        df = df.drop(columns=drop_cols)
        
        hydro_cols = [col for col in df.columns if "Hydro" in col]
        df["Hydro"] = df[hydro_cols].fillna(0).sum(axis=1)
        df = df.drop(columns=hydro_cols)
        return df

    if (source == "sw"):
        return df

    if (source == "tcs_saldo"):
        df.rename(columns={"Czech Republic": "Czechia"}, inplace=True)
        #df["Load"] = df.Load.fillna(0) + df["sum"].fillna(0) #Sum references Load pre 2015

        df.drop(columns="sum", inplace=True)
        iso_codes = {}
        for col in list(set(df.columns) - set(["sum", "year", "hour"])):
            try:
                country = pycountry.countries.get(name=col)
                if country:
                    iso_codes[col] = country.alpha_2
                    print("Country code is: ", country.alpha_2)
                else:
                    raise ValueError("Country not found: ", col)
            except LookupError:
                raise ValueError("Country not found: ", col)
        
        return df.rename(columns=iso_codes)


def prepare_power_dataframe(df, year):
    """
    Detects the frequency of the input dataframe and creates a new index based on the detected frequency. 
    Scales the dataframe to power units in megawatts based on the maximum value. 

    Args:
        df (pandas.DataFrame): The input dataframe to prepare.
        year (int): The year for which the dataframe is prepared.

    Returns:
        pandas.DataFrame: The prepared dataframe with a new index and scaled values.
        
    Raises:
        ValueError: If the frequency of the input dataframe is unknown or the scale is unknown.
    """
    # Detect frequency of dataframe
    if abs(df.shape[0] - 24*365) <= 24:
        freq = "1h"
    elif abs(df.shape[0] - 24*365*4) <= 96:
        freq = "15min"
        df = df
    else:
        raise ValueError(f"Unknown frequency %{df.shape[0]}")
    
    # Create new index
    df.set_index(pd.date_range(start=f"01-01-{year}", end=f"01-01-{year+1}", freq=freq)[:-1], inplace=True)
    
    # Detect scaling of dataframe and scale to power unit to megawatts
    max_val = df.max().max()
    if 1e6 > max_val > 1e3:
        scale = "MW"
    elif 1e3 > max_val > 0:
        print("Scaling up from GW")
        scale = "GW"
        df *= 1e3
    else:
        raise ValueError(f"Unknown scale %{max_val}")

    df["year"] = df.index.year
    df["hour"] = df.index.hour

    return df

def prepare_and_store_capacity(df):
    """
    Prepares and stores the capacity data in the input dataframe.
    Adds a 'year' column to the dataframe to create an index containing years.
    Splits the dataframe into flexible and installed capacity and stores them in separate pickle files.
    
    Args:
        df (pandas.DataFrame): The input dataframe containing capacity data.

    Returns:
        None
    """
    df["year"] = list(range(2024 - df.shape[0]+1, 2025))
    df.set_index("year", inplace=True)
    
    flex_cols = ['Battery Storage (Capacity)', 'Battery Storage (Power)', 'Hydro pumped storage']
    
    df[flex_cols].fillna(0).to_pickle(f"results/germany_flex_capacity_GW_{df.index[0]}_{df.index[-1]}.xz")
    df.drop(columns=flex_cols).to_pickle(f"results/germany_installed_power_GW_{df.index[0]}_{df.index[-1]}.xz")

def prepare_and_store_power(urls, years, res_name, source):
    """
    Prepare and store power data from multiple URLs.

    Args:
        urls (List[str]): A list of URLs to retrieve power data from.
        years (List[int]): A list of years corresponding to the URLs.
        res_name (str): The name of the file to store the concatenated and harmonized dataframe.
        source (str): The source of the power data.

    Returns:
        None
    """
    dfs = []
    for url, a_year in zip(urls, years):
        df = crawl_power_dataframe(options, url)
        df = prepare_power_dataframe(df, a_year)
        dfs.append(df)
    analysis_df = pd.concat(dfs)
    analysis_df = harmonize_columns(analysis_df, source)
    analysis_df.to_pickle(res_name)
    
if __name__ == "__main__":
    # Set up options for headless browsing
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    print("Start reading energy data")
    
    sources = ["public", "tcs_saldo", "total", "entsoe", "sw"]
    
    #Reading historic energy trading, power production, + self consumption, entsoe and Solar/Wind production data 

    for a_source in sources:
        if a_source in ["sw", "public"]:
            years = range(2010, 2024)
        else:
            years = range(2015, 2024)
        urls = [create_energy_url(a_year, a_source) for a_year in years]
        prepare_and_store_power(urls, years, f"results/germany_power_mw_{years[0]}_{years[-1]}_{a_source}.xz", a_source)
        print("Completed soure: ", a_source)

    #Identify trading partner countries and crawl their power production
    trading_df = pd.read_pickle("results/germany_power_mw_2015_2023_tcs_saldo.xz")
    countries = [col for col in trading_df.columns if col not in ["year", "hour"]]
    for a_country in countries:
        years = range(2015, 2024)
        urls = [create_trading_country_url(a_country, a_year) for a_year in years]
        prepare_and_store_power(urls, years, f"results/{a_country}_power_mw_{years[0]}_{years[-1]}_public.xz", "entsoe")
        print("Completed country: ", a_country)

    #Crawl installed power capacity data 
    print("Start reading installed power data")
    
    url = create_capacity_url()
    df = crawl_power_dataframe(options, url)
    prepare_and_store_capacity(df)