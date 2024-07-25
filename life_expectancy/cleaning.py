# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=inconsistent-return-statements

from pathlib import Path
import argparse
from enum import Enum
import pandas as pd

from life_expectancy.region_enum import Region

def load_data(path_to_open) -> pd.DataFrame:
    initial_data = pd.read_csv(path_to_open, sep='\t', header=0)
    return initial_data

def clean_data(initial_data) -> pd.DataFrame:
    initial_data[['unit', 'sex', 'age','region']] = initial_data['unit,sex,age,geo\\time'].str.split(',', expand=True)
    initial_data = initial_data.drop(['unit,sex,age,geo\\time'], axis=1)

    var_columns = initial_data.iloc[:, 62:66]
    var_values = initial_data.iloc[:, :62]
    data = pd.melt(initial_data, id_vars=var_columns, value_vars=var_values,
                        var_name='year', value_name='value')

    if any(not isinstance(x, int) for x in data['year']):
        data['year'] = pd.to_numeric(data['year'], errors='coerce')

    data.dropna(subset=['year'], inplace=True)

    data['value'] = data['value'].str.replace(r'[^0-9.]', '', regex=True)

    if any(not isinstance(x, float) for x in data['value']):
        data['value'] = pd.to_numeric(data['value'], errors='coerce')

    data.dropna(subset=['value'], inplace=True)

    return data

def save_data(df, path_to_save) -> None:
    df.to_csv(path_to_save, index=False)

def main_function(Region: Enum):

    directory = Path(__file__).resolve().parent
    path_to_open = directory / "data" / "eu_life_expectancy_raw.tsv"
    path_to_save = directory / "data" / "pt_life_expectancy.csv"

    initial_data = load_data(path_to_open)
    data = clean_data(initial_data)

    try:
        region_value = Region.PT.name
        data_country = data[data['region'] == region_value]

        save_data(data_country, path_to_save)

        return data_country

    except AttributeError as e:
        print(f"You tried to use an invalid country code -> {e}")

if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type= Enum, default= Region.PT, help="Country code to filter the data")
    args = parser.parse_args()
    main_function(args.country)
