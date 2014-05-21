__author__ = 'ismailsunni'
__project_name = 'stream-feature-extractor'
__filename = 'translate_style.py'
__date__ = '5/21/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import sys
import os

from PyQt4.QtCore import QCoreApplication, QTranslator

from test.utilities_for_testing import get_qgis_app


QGIS_APP = get_qgis_app()

PAR_DIR = os.path.dirname(__file__)
STYLES_DIR = os.path.join(PAR_DIR, '..','styles')
STYLES_DIR = os.path.abspath(STYLES_DIR)
EN_STYLE_NAME = 'nodes'


def main():
    local = sys.argv[1]
    style_file = os.path.join(STYLES_DIR, EN_STYLE_NAME + '.qml')
    print STYLES_DIR
    print style_file

    parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
    dir_path = os.path.abspath(parent_path)
    file_path = os.path.join(
        dir_path, 'i18n', '%s.qm' % local)
    translator = QTranslator()
    translator.load(file_path)
    # noinspection PyCallByClass
    QCoreApplication.installTranslator(translator)

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

    locale_types = [QCoreApplication.translate('@default', x) for x in types]

    f = open(style_file, 'r')
    style = f.read()
    f.close()

    for i in range(len(types)):
        en_name = '"%s"' % types[i]
        locale_name = '"%s"' % locale_types[i]

        style = style.replace(en_name, locale_name)

    locale_style_file = os.path.join(
        STYLES_DIR, EN_STYLE_NAME + '-' + local + '.qml')
    f = open(locale_style_file, 'wt')
    f.write(style)
    f.close()

if __name__ == '__main__':
    main()
