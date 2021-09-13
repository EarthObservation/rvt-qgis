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


class RVTLocalDom(QgsProcessingAlgorithm):
    """
    RVT Local dominance.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    MIN_RADIUS = "MIN_RADIUS"
    MAX_RADIUS = "MAX_RADIUS"
    ANGULAR_RES = "ANGULAR_RES"
    OBSERVER_H = "OBSERVER_H"
    SAVE_AS_8BIT = "SAVE_AS_8BIT"
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTLocalDom()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_ld'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Local dominance')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Local dominance. Calculates Local dominance.")

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
                name="MIN_RADIUS",
                description="Minimum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10,
                minValue=0,
                maxValue=100
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="MAX_RADIUS",
                description="Maximum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=20,
                minValue=0,
                maxValue=100
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="ANGULAR_RES",
                description="Number of angular directions",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=15,
                minValue=4,
                maxValue=32
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="OBSERVER_H",
                description="Height at which we observe the terrain",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.7,
                minValue=0.5,
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
        min_rad = int(self.parameterAsInt(
            parameters,
            self.MIN_RADIUS,
            context
        ))
        max_rad = int(self.parameterAsInt(
            parameters,
            self.MAX_RADIUS,
            context
        ))
        angular_res = int(self.parameterAsInt(
            parameters,
            self.ANGULAR_RES,
            context
        ))
        observer_h = float(self.parameterAsDouble(
            parameters,
            self.OBSERVER_H,
            context
        ))
        save_8bit = bool(self.parameterAsBool(
            parameters,
            self.SAVE_AS_8BIT,
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

        visualization_arr = rvt.vis.local_dominance(dem=dem_arr, min_rad=min_rad, max_rad=max_rad,
                                                    angular_res=angular_res, observer_height=observer_h,
                                                    ve_factor=ve_factor, no_data=no_data)
        if not save_8bit:
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_arr, e_type=6, no_data=np.nan)
        else:
            visualization_8bit_arr = rvt.default.DefaultValues().float_to_8bit(float_arr=visualization_arr,
                                                                               vis="local dominance")
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_8bit_arr, e_type=1, no_data=np.nan)

        result = {self.OUTPUT: visualization_path}
        return result
