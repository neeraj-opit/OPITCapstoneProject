def compare_columns(sf, laweb):
    sf_cols = set(sf.columns)
    laweb_cols = set(laweb.columns)

    missing_in_laweb = sorted(sf_cols - laweb_cols)
    missing_in_sf = sorted(laweb_cols - sf_cols)
    common_cols = sorted(sf_cols & laweb_cols)

    return missing_in_laweb, missing_in_sf, common_cols
