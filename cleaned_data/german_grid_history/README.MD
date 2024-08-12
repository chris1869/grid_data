## Data Description

All data is stored in a compressed xz format of a pandas dataframe. 
Please use pandas 2.0.0 or higher. to ensure that the data can be read.

```python

import pandas as pd

df = pd.read_pickle("germany_power_mw_2010_2023_public.xz")

```

### 1.0 German power generation in megawatts (cleaned_data/german_grid_history)

#### 1.1. germany_power_mw_2010_2023_public.xz

- Measure: Net electricity production of plants for public electricity production.
- Time horizon: Years 2010 to 2023 (incl.)
- Unit: power in megawatts
- Granularity: 2010 - 2014 (hourly); 2015 - 2023 (15min)
- Datatype: Compressed pandas dataframe
- Data sources: ENTSO-E, AGEE-Stat, Destatis, Fraunhofer ISE, AG Energiebilanzen
- Crawled via: https://www.energy-charts.info/charts/power/chart.htm?l=en&c=DE&interval=year&year=2023&source=public

#### 1.2. germany_power_mw_2015_2023_entsoe.xz

- Measure: Net electricity production of plants for public electricity production.
- Time horizon: Years 2015 to 2023 (incl.)
- Unit: power in megawatts
- Granularity: 2015 - 2023 (15min)
- Datatype: Compressed pandas dataframe
- Data sources: ENTSO-E
- Crawled via: https://www.energy-charts.info/charts/power/chart.htm?l=en&c=DE&interval=year&year=2023&source=entsoe

#### 1.3. germany_power_mw_2015_2023_total.xz

- Measure: Net electricity production of plants for public electricity production and industrial plants.
- Time horizon: Years 2015 to 2023 (incl.)
- Unit: power in megawatts
- Granularity: 2015 - 2023 (15min)
- Datatype: Compressed pandas dataframe
- Data sources: ENTSO-E, AG Energiebilanzen, BDEW
- Crawled via: https://www.energy-charts.info/charts/power/chart.htm?l=en&c=DE&interval=year&year=2023&source=total

#### 1.4. germany_power_mw_2015_2023_sw.xz

- Measure: Wind and solar electricity production in the 4 transmission areas in Germany.
- Time horizon: Years 2010 to 2023 (incl.)
- Unit: power in megawatts
- Granularity: 2010 - 2014 (hourly); 2015 - 2023 (15min)
- Datatype: Compressed pandas dataframe
- Data sources: 50Hertz, Amprion, TenneT, TransnetBW, ENTSO-E
- Crawled via: https://www.energy-charts.info/charts/power/chart.htm?l=en&c=DE&interval=year&year=2023&source=sw

### 2. German installed capacity (cleaned_data/german_grid_history)

#### 2.1. germany_installed_power_GW_2002_2024.xz

- Measure: Installed power capacity of different energy sources in Germany.
- Time horizon: Years 2002 to 2024 (incl.)
- Unit: power in gigawatts
- Granularity: annual maximum
- Datatype: Compressed pandas dataframe
- Data sources: 50Hertz, Amprion, TenneT, TransnetBW, ENTSO-E
- Crawled via: https://www.energy-charts.info/charts/installed_power/chart.htm?l=en&c=DE&interval=year&year=-1

#### 2.2. germany_flex_capacity_GW_2002_2024.xz

- Measure: Installed power capacity of different flexibility sources in Germany (battery, hydro).
- Time horizon: Years 2002 to 2024 (incl.)
- Unit: power in gigawatts
- Granularity: annual maximum
- Datatype: Compressed pandas dataframe
- Data sources: 50Hertz, Amprion, TenneT, TransnetBW, ENTSO-E
- Crawled via: https://www.energy-charts.info/charts/installed_power/chart.htm?l=en&c=DE&interval=year&year=-1
