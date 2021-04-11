from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean)
from qgis import processing
import numpy as np
import rvt.default
import rvt.vis


class RVTMsrm(QgsProcessingAlgorithm):
    """
    RVT Multi-scale relief model.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    FEATURE_MIN = "FEATURE_MIN"
    FEATURE_MAX = "FEATURE_MAX"
    SCALING_FACTOR = "SCALING_FACTOR"
    SAVE_AS_8BIT = "SAVE_AS_8BIT"
    FILL_NO_DATA = "FILL_NO_DATA"
    FILL_METHOD = "FILL_METHOD"
    KEEP_ORIG_NO_DATA = "KEEP_ORIG_NO_DATA"
    OUTPUT = 'OUTPUT'

    fill_method_options = ["idw_20_2", "kd_tree", "nearest_neighbour"]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTMsrm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_msrm'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Multi-scale relief model')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Multi-scale relief model. Calculates Multi-scale relief model.")

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
                name="FEATURE_MIN",
                description="Feature minimum",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1,
                minValue=0,
                maxValue=1000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="FEATURE_MAX",
                description="Feature maximum",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=5,
                minValue=0,
                maxValue=1000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="SCALING_FACTOR",
                description="Scaling factor",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=3,
                minValue=1,
                maxValue=20
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
            QgsProcessingParameterEnum(
                name="FILL_METHOD",
                description="Fill no-data method.",
                options=self.fill_method_options,
                defaultValue=self.fill_method_options[0]
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
        feature_min = float(self.parameterAsDouble(
            parameters,
            self.FEATURE_MIN,
            context
        ))
        feature_max = float(self.parameterAsDouble(
            parameters,
            self.FEATURE_MAX,
            context
        ))
        scaling_factor = int(self.parameterAsDouble(
            parameters,
            self.SCALING_FACTOR,
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
        fill_method_enum = int(self.parameterAsEnum(
            parameters,
            self.FILL_METHOD,
            context
        ))
        fill_method = self.fill_method_options[fill_method_enum]
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

        visualization_arr = rvt.vis.msrm(dem=dem_arr, resolution=resolution[0], feature_min=feature_min,
                                         feature_max=feature_max, scaling_factor=scaling_factor,
                                         ve_factor=ve_factor, no_data=no_data,
                                         fill_no_data=fill_no_data, fill_method=fill_method,
                                         keep_original_no_data=keep_orig_no_data)
        if not save_8bit:
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_arr, e_type=6, no_data=np.nan)
        else:
            visualization_8bit_arr = rvt.default.DefaultValues().float_to_8bit(float_arr=visualization_arr,
                                                                               vis="multi-scale relief model")
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_8bit_arr, e_type=1, no_data=np.nan)

        result = {self.OUTPUT: visualization_path}
        return result
