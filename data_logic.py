# data_logic.py

import pandas as pd

def remove_duplicates_logic(df):
    """Returns a new DataFrame with duplicate rows removed."""
    if df is None:
        return None
    return df.drop_duplicates()

def handle_missing_values_logic(df, column, action, custom_value=None):
    """Returns a new DataFrame with missing values handled."""
    if df is None or not column or not action:
        return df

    df_copy = df.copy()

    if action == "Drop Rows":
        df_copy.dropna(subset=[column], inplace=True)
    elif action in ["Fill with Mean", "Fill with Median"]:
        if pd.api.types.is_numeric_dtype(df_copy[column]):
            fill_value = df_copy[column].mean() if action == "Fill with Mean" else df_copy[column].median()
            df_copy[column].fillna(fill_value, inplace=True)
        else:
            raise TypeError(f"{action} can only be used on numeric columns.")
    elif action == "Fill with Mode":
        df_copy[column].fillna(df_copy[column].mode()[0], inplace=True)
    elif action == "Fill with Value:":
        df_copy[column].fillna(custom_value, inplace=True)

    return df_copy