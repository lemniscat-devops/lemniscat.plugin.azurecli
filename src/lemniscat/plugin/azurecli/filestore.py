# -*- coding: utf-8 -*-
# above is for compatibility of python2.7.11

import logging
import os
import subprocess, sys   
from lemniscat.core.util.helpers import LogUtil
import re

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.setLoggerClass(LogUtil)
log = logging.getLogger(__name__.replace('lemniscat.', ''))

class FileStore:
    def __init__(self):
        pass
            
    # save dict to yaml file
    @staticmethod
    def saveYamlFile(filePath, data: dict) -> None:
        import yaml
        with open(filePath, 'w') as stream:
            try:
                yaml.dump(data, stream)
            except yaml.YAMLError as exc:
                log.error(exc)

    # save dict to json file
    @staticmethod
    def saveJsonFile(filePath, data: dict) -> None:
        import json
        with open(filePath, 'w') as stream:
            try:
                json.dump(data, stream)
            except json.JSONDecodeError as exc:
                log.error(exc)