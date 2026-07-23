# coding=utf-8
"""Tests QGIS plugin init."""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/10/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import unittest
import logging
import configparser
import importlib.util
from unittest import mock

LOGGER = logging.getLogger('QGIS')

PLUGIN_INIT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, '__init__.py'))
PLUGIN_INIT_SPEC = importlib.util.spec_from_file_location(
    'rvt_qgis_init', PLUGIN_INIT_PATH)
PLUGIN_INIT = importlib.util.module_from_spec(PLUGIN_INIT_SPEC)
PLUGIN_INIT_SPEC.loader.exec_module(PLUGIN_INIT)


class TestInit(unittest.TestCase):
    """Test that the plugin init is usable for QGIS.

    Based heavily on the validator class by Alessandro
    Passoti available here:

    http://github.com/qgis/qgis-django/blob/master/qgis-app/
             plugins/validator.py

    """

    def test_check_dependencies_reports_missing_packages(self):
        """The initializer should report both required Python packages."""
        with mock.patch.object(PLUGIN_INIT.importlib, 'import_module', side_effect=ImportError('boom')):
            unavailable = PLUGIN_INIT._check_dependencies()

        self.assertEqual([item['name'] for item in unavailable], ['Matplotlib', 'SciPy'])

    def test_read_init(self):
        """Test that the plugin __init__ will validate on plugins.qgis.org."""

        # You should update this list according to the latest in
        # https://github.com/qgis/qgis-django/blob/master/qgis-app/
        #        plugins/validator.py

        required_metadata = [
            'name',
            'description',
            'version',
            'qgisMinimumVersion',
            'email',
            'author']

        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.pardir,
            'metadata.txt'))
        LOGGER.info(file_path)
        metadata = []
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(file_path)
        message = 'Cannot find a section named "general" in %s' % file_path
        assert parser.has_section('general'), message
        metadata.extend(parser.items('general'))

        for expectation in required_metadata:
            message = ('Cannot find metadata "%s" in metadata source (%s).' % (
                expectation, file_path))

            self.assertIn(expectation, dict(metadata), message)

if __name__ == '__main__':
    unittest.main()
