def compare_ids(sf, laweb, pk):
    sf_ids = set(sf[pk])
    laweb_ids = set(laweb[pk])

    only_in_sf = sorted(sf_ids - laweb_ids)
    only_in_laweb = sorted(laweb_ids - sf_ids)

    return only_in_sf, only_in_laweb

