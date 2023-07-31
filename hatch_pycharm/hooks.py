from hatchling.plugin import hookimpl

from hatch_pycharm.plugin import PycharmEnvironment


@hookimpl
def hatch_register_environment():
    return PycharmEnvironment
