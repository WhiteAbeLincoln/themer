from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = "undefined"
    pass

from .lib import (
    main, vprint, render_template, get_config_home
)
