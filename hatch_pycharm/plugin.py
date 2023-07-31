from hatch.env.virtual import VirtualEnvironment

from ._pycharm import make_open_file_command


class PycharmEnvironment(VirtualEnvironment):
    PLUGIN_NAME = "pycharm"

    def create(self):
        super().create()
        self.platform.check_command(make_open_file_command(self.root))
        self.app.display_success("We opened the self.root directory as a project hopefully")
