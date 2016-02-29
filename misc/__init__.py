from os.path import dirname, basename, isfile

import glob
all = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in all if isfile(f)]
