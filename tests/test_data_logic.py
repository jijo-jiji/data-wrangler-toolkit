# tests/test_data_logic.py

import pandas as pd
import numpy as np
import pytest
from data_logic import remove_duplicates_logic, handle_missing_values_logic

def test_remove_duplicates_logic():
    """Tests if the remove_duplicates_logic function works correctly."""
    # Arrange: Create a DataFrame with known duplicates
    data = {'colA': [1, 2, 2, 3], 'colB': ['x', 'y', 'y', 'z']}
    test_df = pd.DataFrame(data)

    # Act: Run the function
    result_df = remove_duplicates_logic(test_df)

    # Assert: Check if the result is as expected
    assert len(result_df) == 3
    assert result_df.shape == (3, 2)
    # Check that the second row is what remains
    assert result_df.iloc[1]['colA'] == 2

def test_handle_missing_values_drop_rows():
    """Tests dropping rows with missing values."""
    # Arrange
    data = {'colA': [1, np.nan, 3], 'colB': ['x', 'y', 'z']}
    test_df = pd.DataFrame(data)

    # Act
    result_df = handle_missing_values_logic(test_df, column='colA', action='Drop Rows')

    # Assert
    assert len(result_df) == 2
    assert np.nan not in result_df['colA'].values

def test_handle_missing_values_fill_mean():
    """Tests filling missing values with the mean."""
    # Arrange
    data = {'colA': [10, 20, np.nan]}
    test_df = pd.DataFrame(data)

    # Act
    result_df = handle_missing_values_logic(test_df, column='colA', action='Fill with Mean')

    # Assert
    assert result_df.iloc[2]['colA'] == 15.0 # Mean of 10 and 20 is 15

def test_handle_missing_values_raises_error_for_mean_on_text():
    """Tests that filling mean on a non-numeric column raises a TypeError."""
    # Arrange
    data = {'colA': ['cat', 'dog', None]}
    test_df = pd.DataFrame(data)

    # Act & Assert
    with pytest.raises(TypeError):
        handle_missing_values_logic(test_df, column='colA', action='Fill with Mean')