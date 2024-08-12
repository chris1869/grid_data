## Data description

All data is stored in a compressed xz format of a pandas dataframe. The majority of the data has been converted into category types, so you don't need to convert the numerical values into their String equivalents (e.g., orientation value of 452 means "South"). 

```python

import pandas as pd

df = pd.read_pickle("EinheitenSolar.xz")

```

Please use pandas 2.0.0 or higher. to ensure that the data can be read.

### 1. Einheiten

The files starting with Einheiten are probably the best starting point for understanding this vast dataset on the different Solar sources. For more details on what is included in this data, please refer to raw_data/market_master_data/xsd/*.xsd which includes a detailed description of the data.
