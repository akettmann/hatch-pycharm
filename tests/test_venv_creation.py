def test_jdk_element_matches(jdk_element, test_venv):
    assert test_venv._build_jdk_element() == jdk_element


def test_misc_element_matches(misc_element, test_venv):
    assert test_venv._build_misc_element() == misc_element
