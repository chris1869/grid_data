## Data description

All data is stored in a compressed xz format of a pandas dataframe. 
Please use pandas 2.0.0 or higher. to ensure that the data can be read.

```python

import pandas as pd

df = pd.read_pickle("germany_power_mw_2015_2023_tcs_saldo.xz")

```

### 1. German electricity import/export (cleaned_data/electricity_trading)

#### 1.1. germany_power_mw_2015_2023_tcs_saldo.xz

- Measure: Electricity import and export per country (trading - no physical flows)
- Time horizon: Years 2015 to 2023 (incl.)
- Unit: power in megawatts
- Granularity: 15min intervalls
- Datatype: Compressed pandas dataframe
- Data sources: 
- Crawled via: 

#### 1.2. %COUNTRY_CODE_power_mw_2015_2023_public.xz
- Measure: Net electricity production of plants for public electricity production for country %COUNTRY_CODE
- Time horizon: Years 2015 to 2023 (incl.)
- Unit: power in megawatts
- Granularity: 15min intervalls
- Datatype: Compressed pandas dataframe
- Data sources: Depends on country
- Crawled via: https://www.energy-charts.info/charts/power/chart.htm?l=en&c=BE&interval=year&year=2023&source=public
- Countries: Austria (AT), Belgium (BE), Switzerland (CH), Czechia (CZ), Denmark (DK), France (FR), Luxembourg (LU), Netherlands (NL), Norway (NO), Poland (PL), Sweden (SE)
