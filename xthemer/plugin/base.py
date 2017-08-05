import abc


class XThemerPlugin(object, metaclass=abc.ABCMeta):
    """Base class for a xthemer module plugin
    """

    def __init__(self, **kwargs):
        if 'colors' in kwargs:
            self.colors = kwargs['colors']
        if 'dir' in kwargs:
            self.dir = kwargs['dir']

    @abc.abstractmethod
    def run(self):
        """Plugin entry point
        """
