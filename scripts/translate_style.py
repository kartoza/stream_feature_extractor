# -*- coding: utf-8 -*-
"""**Script for translating qml style file.**

.. tip::
   Detailed multi-paragraph description...

"""
from __future__ import division

__author__ = 'Ismail Sunni <ismail@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '21/05/2014'
__license__ = "GPL"
__copyright__ = ''


import sys
import os

from PyQt4.QtCore import QCoreApplication, QTranslator

from test.utilities_for_testing import get_qgis_app


QGIS_APP = get_qgis_app()

PAR_DIR = os.path.dirname(__file__)
STYLES_DIR = os.path.join(PAR_DIR, '..', 'styles')
STYLES_DIR = os.path.abspath(STYLES_DIR)
EN_STYLE_NAME = 'nodes'


def main():
    locales = sys.argv[1:]
    style_file = os.path.join(STYLES_DIR, EN_STYLE_NAME + '.qml')
    parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
    dir_path = os.path.abspath(parent_path)

    types = [
        'Well',
        'Sink',
        'Branch',
        'Confluence',
        'Pseudo node',
        'Watershed',
        'Unclear Bifurcation',
        'Self Intersection',
        'Segment Center',
        'Intersection'
    ]

    f = open(style_file, 'r')
    style = f.read()
    f.close()

    for local in locales:
        print 'Compiling style for %s' % local
        file_path = os.path.join(dir_path, 'i18n', '%s.qm' % local)
        translator = QTranslator()
        translator.load(file_path)
        # noinspection PyCallByClass
        QCoreApplication.installTranslator(translator)

        locale_types = [
            QCoreApplication.translate('@default', x) for x in types]

        locale_style = style

        for i in range(len(types)):
            en_name = '"%s"' % types[i]
            locale_name = '"%s"' % locale_types[i]

            locale_style = locale_style.replace(en_name, locale_name)

        locale_style_file = os.path.join(
            STYLES_DIR, EN_STYLE_NAME + '-' + local + '.qml')
        f = open(locale_style_file, 'wt')
        f.write(locale_style)
        f.close()

if __name__ == '__main__':
    main()
