# coding=utf-8
"""Entry point for program"""

from __future__ import print_function
import sys

from arcturus.ArcturusCore import PYTHON_REQUIRED_MAJOR, PYTHON_REQUIRED_MINOR

if __name__ == '__main__':
    if sys.version_info[0] >= PYTHON_REQUIRED_MAJOR and sys.version_info[1] >= PYTHON_REQUIRED_MINOR:
        import arcturus.commandline as commandline

        commandline.main()
    else:
        print("python %d.%d or newer is required!" % (PYTHON_REQUIRED_MAJOR, PYTHON_REQUIRED_MINOR), file=sys.stderr)
