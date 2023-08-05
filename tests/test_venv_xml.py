def test_jdk_element_matches(jdk_element, test_venv):
    test_venv.name = "Python 3.11 (hatch-pycharm)"

    assert test_venv._build_jdk_element() == jdk_element


def test_misc_element_matches(misc_element, test_venv):
    project = misc_element
    assert len(misc_element) == 1
    component = project[0]
    assert component.attrib["project-jdk-name"] == test_venv.name
    assert component.attrib["project-jdk-type"] == "Python SDK"


def test_parses_our_version_number(test_venv):
    import sys

    assert test_venv.exe_version == sys.version_info[:3]


def test__helpers_dir_roots(test_venv):
    print(test_venv.build_jdk_xml())


def test_from_json_str(config_vars):
    import sysconfig

    for k, v in sysconfig.get_config_vars().items():
        assert getattr(config_vars, k) == v
