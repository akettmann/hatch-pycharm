import subprocess

import pytest
from click.testing import CliRunner


class TestException(BaseException):
    pass


@pytest.fixture(autouse=True)
def no_subprocess_run(monkeypatch):
    original_subprocess_run = subprocess.run
    # noinspection PyProtectedMember
    import hatch_pycharm._pycharm.paths as paths

    platform_name = paths.platform_exe_name()

    def mock_subprocess_run(*args, **kwargs):
        if args and args[0] and args[0][0].endswith(platform_name):
            msg = f"subprocess.run was called with '{paths.platform_exe_name()}'"
            raise TestException(msg)
        else:
            return original_subprocess_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)


def test_subprocess_run_is_called(new_project):
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
