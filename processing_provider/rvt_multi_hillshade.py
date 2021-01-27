from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterBoolean)
from qgis import processing
import numpy as np
import rvt.default
import rvt.vis


class RVTMultiHillshade(QgsProcessingAlgorithm):
    """
    RVT Multiple directions hillshade.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    NUM_DIRECTIONS = 'NUM_DIRECTIONS'
    SUN_ELEVATION = 'SUN_ELEVATION'
    SAVE_AS_8BIT = "SAVE_AS_8BIT"
    FILL_NO_DATA = "FILL_NO_DATA"
    KEEP_ORIG_NO_DATA = "KEEP_ORIG_NO_DATA"
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTMultiHillshade()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_multi_hillshade'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Multiple directions hillshade')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Multiple direction hillshade."
                       " Calculates hillshade in multiple directions.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input DEM raster layer'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="VE_FACTOR",
                description="Vertical exaggeration factor",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1,
                minValue=-1000,
                maxValue=1000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="NUM_DIRECTIONS",
                description="Number of solar azimuth angles (bands).",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=16,
                minValue=2,
                maxValue=64
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="SUN_ELEVATION",
                description="Solar vertical angle (above the horizon) in degrees.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=35,
                minValue=0,
                maxValue=90
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name="SAVE_AS_8BIT",
                description="Save as 8bit raster",
                defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name="FILL_NO_DATA",
                description="Fill no-data (holes)",
                defaultValue=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name="KEEP_ORIG_NO_DATA",
                description="Keep original no-data",
                defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Output visualization raster layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        dem_layer = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )

        ve_factor = float(self.parameterAsDouble(
            parameters,
            self.VE_FACTOR,
            context
        ))
        nr_dir = int(self.parameterAsInt(
            parameters,
            self.NUM_DIRECTIONS,
            context
        ))
        sun_elevation = float(self.parameterAsDouble(
            parameters,
            self.SUN_ELEVATION,
            context
        ))
        save_8bit = bool(self.parameterAsBool(
            parameters,
            self.SAVE_AS_8BIT,
            context
        ))
        fill_no_data = bool(self.parameterAsBool(
            parameters,
            self.FILL_NO_DATA,
            context
        ))
        keep_orig_no_data = bool(self.parameterAsBool(
            parameters,
            self.KEEP_ORIG_NO_DATA,
            context
        ))
        visualization_path = (self.parameterAsOutputLayer(
            parameters,
            self.OUTPUT,
            context,
        ))

        dem_path = str(dem_layer.source())

        dict_arr_dem = rvt.default.get_raster_arr(dem_path)
        resolution = dict_arr_dem["resolution"]  # (x_res, y_res)
        dem_arr = dict_arr_dem["array"]
        no_data = dict_arr_dem["no_data"]

        visualization_arr = rvt.vis.multi_hillshade(dem=dem_arr, resolution_x=resolution[0], resolution_y=resolution[1],
                                                    nr_directions=nr_dir, sun_elevation=sun_elevation,
                                                    ve_factor=ve_factor, no_data=no_data,
                                                    fill_no_data=fill_no_data, keep_original_no_data=keep_orig_no_data)
        if not save_8bit:
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_arr, e_type=6, no_data=np.nan)
        else:
            default = rvt.default.DefaultValues()  # we have to use this class to calculate 8bit
            default.fill_no_data = fill_no_data
            default.keep_original_no_data = keep_orig_no_data
            visualization_8bit_arr = default.float_to_8bit(float_arr=dem_arr, vis="multiple directions hillshade",
                                                           x_res=resolution[0], y_res=resolution[1],
                                                           no_data=no_data)
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_8bit_arr, e_type=1, no_data=np.nan)

        result = {self.OUTPUT: visualization_path}
        return result
