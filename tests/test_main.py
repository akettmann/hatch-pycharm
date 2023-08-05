import subprocess
from pathlib import Path
from unittest.mock import MagicMock, ANY

import pytest
from click.testing import CliRunner


class TestException(BaseException):
    pass


@pytest.fixture()
def mock_run(monkeypatch) -> MagicMock:
    from unittest.mock import create_autospec

    original_subprocess_run = subprocess.run
    # noinspection PyProtectedMember
    import hatch_pycharm._pycharm.paths as paths

    platform_name = paths.platform_exe_name()

    def mock_func(*args, **kwargs):
        if args and args[0] and args[0][0].endswith(platform_name):
            msg = f"subprocess.run was called with '{paths.platform_exe_name()}'"
            raise TestException(msg)
        else:
            return original_subprocess_run(*args, **kwargs)

    from subprocess import run

    mock_subprocess_run = create_autospec(run, side_effect=mock_func)
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    yield mock_subprocess_run


def test_subprocess_run_is_called(new_project, mock_run):
    """
    .. function:: test_subprocess_run_is_called(new_project) -> None

        This function tests if the `subprocess.run()` method is called correctly. This will detect when our oh so
         fragile "interface" with hatch is broken.

        :param new_project: The new project to be tested, a fixture
        :type new_project: Any

        :raises TestException: If the `subprocess.run()` method is not called correctly.


    """
    from hatch.cli import hatch

    runner = CliRunner()
    with pytest.raises(TestException):
        # noinspection PyTypeChecker
        runner.invoke(hatch, ["run", "echo", "a"], catch_exceptions=False)
    mock_run.assert_called_once()
    exe_location, detected_location = map(Path, mock_run.call_args[0][0])
    assert detected_location == new_project
    assert exe_location.is_file()
