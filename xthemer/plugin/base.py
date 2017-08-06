import abc
import logging
from termcolor import colored
from xthemer import config
from typing import Optional, Dict, Union

Colors = Dict[str, Union[str, float]]

# this plugin system borrows pretty heavily from beets
# see https://github.com/beetbox/beets/blob/master/beets/plugins.py

log = logging.getLogger('xthemer')


class PluginLogFilter(logging.Filter):
    """A logging filter that appends the plugin name
    to the message
    """
    def __init__(self, plugin):
        super(PluginLogFilter, self).__init__()
        self.prefix = "{}: ".format(plugin.name)

    def filter(self, record):
        prefix = colored(self.prefix, "green", attrs=["bold"])
        if hasattr(record.msg, "msg") and isinstance(record.msg.msg, str):
            record.msg.msg = prefix + record.msg.msg
        elif isinstance(record.msg, str):
            record.msg = prefix + record.msg
        return True


class XThemerPlugin(object, metaclass=abc.ABCMeta):
    """Base class for a xthemer module plugin
    Plugins can provide functionality by defining a
    subclass of XThemerPlugin and overriding the
    run method defined here
    """

    def __init__(self, name: str, colors: Colors, directory: str):
        """
        Initializes the XThemerPlugin object
        :type name: str
        :type colors: Dict[str, Union[str, float]]
        :type directory: Optional[str]
        """
        self.name = name or self.__module__.split('.')[-1]
        self.config = config[self.name]
        self.colors = colors
        self.directory = directory

        self._log: logging.Logger = log.getChild(self.name)
        self._log.setLevel(logging.NOTSET)
        if not any(isinstance(f, PluginLogFilter) for f in self._log.filters):
            self._log.addFilter(PluginLogFilter(self))

    @abc.abstractmethod
    def run(self):
        """Plugin entry point
        Called by xthemer when running plugins
        """
