from qgis.core import QgsProcessingProvider

from processing_provider.rvt_hillshade import RVTHillshade
from processing_provider.rvt_multi_hillshade import RVTMultiHillshade
from processing_provider.rvt_slope import RVTSlope
from processing_provider.rvt_slrm import RVTSlrm
from processing_provider.rvt_svf import RVTSvf
from processing_provider.rvt_asvf import RVTASvf
from processing_provider.rvt_opns import RVTOpns
from processing_provider.rvt_sky_illum import RVTSim
from processing_provider.rvt_local_dom import RVTLocalDom
from processing_provider.rvt_blender import RVTBlender
from processing_provider.rvt_msrm import RVTMsrm


class Provider(QgsProcessingProvider):
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(RVTHillshade())
        self.addAlgorithm(RVTMultiHillshade())
        self.addAlgorithm(RVTSlope())
        self.addAlgorithm(RVTSlrm())
        self.addAlgorithm(RVTSvf())
        self.addAlgorithm(RVTASvf())
        self.addAlgorithm(RVTOpns())
        # self.addAlgorithm(RVTSim())
        self.addAlgorithm(RVTLocalDom())
        self.addAlgorithm(RVTBlender())
        self.addAlgorithm(RVTMsrm())

    def id(self, *args, **kwargs):
        """The ID of your plugin, used for identifying the provider.

        This string should be a unique, short, character only string,
        eg "qgis" or "gdal". This string should not be localised.
        """
        return 'rvt'

    def name(self, *args, **kwargs):
        """The human friendly name of your plugin in Processing.

        This string should be as short as possible (e.g. "Lastools", not
        "Lastools version 1.0.1 64-bit") and localised.
        """
        return self.tr('Relief visualization toolbox')

    def icon(self):
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)
