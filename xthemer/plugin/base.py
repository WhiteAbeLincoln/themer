import abc


class PluginBase(object, metaclass=abc.ABCMeta):
    """Base class for a xthemer module plugin
    """

    def __init__(self, colors, directory):
        self.colors = colors
        self.dir = directory

    @abc.abstractmethod
    def run(self):
        """Plugin entry point
        """
