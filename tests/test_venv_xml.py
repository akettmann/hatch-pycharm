def test_jdk_element_matches(jdk_element, current_project_venv):
    current_project_venv.name = "Python 3.11 (hatch-pycharm)"

    assert current_project_venv._build_jdk_element() == jdk_element


def test_misc_element_matches(current_project_misc_file, current_project_venv):
    project = current_project_misc_file
    pr_component = project.find("component[@name='ProjectRootManager']")
    assert pr_component.attrib["project-jdk-name"] == current_project_venv.name
    assert pr_component.attrib["project-jdk-type"] == "Python SDK"


def test_parses_our_version_number(current_project_venv):
    import sys

    assert current_project_venv.exe_version == sys.version_info[:3]


def test__helpers_dir_roots(current_project_venv):
    print(current_project_venv.build_jdk_xml())


def test_from_json_str(config_vars):
    import sysconfig

    for k, v in sysconfig.get_config_vars().items():
        assert getattr(config_vars, k) == v
