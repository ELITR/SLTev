#!/usr/bin/env python
import pkg_resources
import sys

sltev_home = pkg_resources.resource_filename('SLTev', '')
sys.path.insert(1, sltev_home)

__version__ = "1.1.6"

