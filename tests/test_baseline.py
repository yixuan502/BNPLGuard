"""Portable target-mapping checks; historical raw-data checks are held separately."""
import numpy as np
import pandas as pd
import pytest
from src.preprocessing import map_target

def test_labels_exclude_missing_and_refuse_unknown():
    result=map_target(pd.Series([1,2,3,-1,np.nan]))
    assert result.iloc[:3].tolist()==[0,1,1]
    assert result.iloc[3:].isna().all()
    with pytest.raises(ValueError):map_target(pd.Series([0]))
