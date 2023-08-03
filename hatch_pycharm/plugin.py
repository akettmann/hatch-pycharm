from pathlib import Path

from hatch.env.collectors.plugin.interface import EnvironmentCollectorInterface
from hatch.env.virtual import VirtualEnvironment
from hatch.template.plugin.interface import TemplateInterface
from functools import partial
import subprocess
from ._pycharm import make_open_file_command


def open_pycharm(location: Path):
    cmd: list[str] = list(make_open_file_command(location))
    subprocess.run(cmd, check=True)


class PycharmEnvironment(VirtualEnvironment):
    PLUGIN_NAME = "pycharm"

    def create(self):
        super().create()
        self.platform.check_command(make_open_file_command(self.root))
        self.app.display_success("We opened the self.root directory as a project hopefully")


class PycharmTemplate(TemplateInterface):
    """This isn't a good idea, but it is an idea. We are not templating with this, we are throwing a callback on the
    end of the Click context with `click.get_current_context(),
    ref:https://click.palletsprojects.com/en/8.1.x/advanced/#managing-resources"""

    PLUGIN_NAME = "pycharm"

    @staticmethod
    def copy_what_new_does(name, location, initialize):
        """Copy pasted the load bearing parts from the hatch code. Shamelessly."""
        if location:
            location = Path(location).resolve()
        if initialize:
            location = location or Path.cwd()
        if not location:
            from hatch.project.core import Project

            normalized_name = Project.canonicalize_name(name, strict=False)
            location = Path(normalized_name).resolve()
        return location

    def finalize_files(self, config, files):
        """We aren't finalizing anything, we are just registering a call on close hook"""
        from click import get_current_context

        # Get the execution context from Click
        ctx = get_current_context()
        # Get the params we need from the context
        name = ctx.params.get("name")
        location = ctx.params.get("location")
        initialize = ctx.params.get("initialize")
        # Get the processed version of location based on one reading of the code one time
        # This isn't fragile!!!
        location = self.copy_what_new_does(name, location, initialize)
        # Tell Click to call us when this context is done (When the new command is closed out)
        ctx.call_on_close(partial(open_pycharm, location))


class PycharmCollector(EnvironmentCollectorInterface):
    PLUGIN_NAME = "pycharm"
