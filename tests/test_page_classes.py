from hydro_yearbook_digitizer.page_classes import PageClass, route_page


def test_map_is_explicitly_excluded():
    route = route_page(PageClass.MAP)
    assert route.excluded_from_ocr is True
    assert route.extract_table is False


def test_cover_extracts_identity_not_table():
    route = route_page(PageClass.COVER)
    assert route.extract_metadata is True
    assert route.extract_table is False


def test_variable_index_is_extracted():
    route = route_page(PageClass.VARIABLE_INDEX)
    assert route.extract_table is True
