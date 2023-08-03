from hatchling.plugin import hookimpl

from hatch_pycharm.plugin import PycharmEnvironment, PycharmTemplate, PycharmCollector


@hookimpl
def hatch_register_environment():
    return PycharmEnvironment


@hookimpl
def hatch_register_template():
    return PycharmTemplate


@hookimpl
def hatch_register_environment_collector():
    return PycharmCollector
