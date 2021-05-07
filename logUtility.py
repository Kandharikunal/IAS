import os.path
from os import path
import json


def checkLogFileExists(fileName):
    if path.exists(fileName):
        if (os.path.getsize(fileName) > 0):
            return True
        else:
            return False
    else:
        return False