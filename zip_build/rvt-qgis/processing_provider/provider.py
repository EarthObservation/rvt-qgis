from qgis.core import QgsProcessingProvider

from .rvt_hillshade import RVTHillshade
from .rvt_multi_hillshade import RVTMultiHillshade
from .rvt_slope import RVTSlope
from .rvt_slrm import RVTSlrm
from .rvt_svf import RVTSvf
from .rvt_asvf import RVTASvf
from .rvt_opns import RVTOpns
from .rvt_sky_illum import RVTSim
from .rvt_local_dom import RVTLocalDom
from .rvt_blender import RVTBlender
from .rvt_msrm import RVTMsrm
from .rvt_mstp import RVTMstp
from .rvt_fill_no_data import RVTFillNoData, RVTFillNoDataIDW


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
        self.addAlgorithm(RVTMstp())
        self.addAlgorithm(RVTFillNoData())
        self.addAlgorithm(RVTFillNoDataIDW())

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
