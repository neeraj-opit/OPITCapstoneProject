def compare_dtypes(sf, laweb, common_cols):
    mismatches = []

    for col in common_cols:
        sf_type = str(sf[col].dtype)
        laweb_type = str(laweb[col].dtype)
        if sf_type != laweb_type:
            mismatches.append({
                "column": col,
                "sf_dtype": sf_type,
                "laweb_dtype": laweb_type
            })

    return mismatches

