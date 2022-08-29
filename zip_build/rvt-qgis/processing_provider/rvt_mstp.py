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
from rvt.default import RVTVisualization


class RVTMstp(QgsProcessingAlgorithm):
    """
    RVT Multi-scale topographic position.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    LOCAL_SCALE_MIN = "LOCAL_SCALE_MIN"
    LOCAL_SCALE_MAX = "LOCAL_SCALE_MAX"
    LOCAL_SCALE_STEP = "LOCAL_SCALE_STEP"
    MESO_SCALE_MIN = "MESO_SCALE_MIN"
    MESO_SCALE_MAX = "MESO_SCALE_MAX"
    MESO_SCALE_STEP = "MESO_SCALE_STEP"
    BROAD_SCALE_MIN = "BROAD_SCALE_MIN"
    BROAD_SCALE_MAX = "BROAD_SCALE_MAX"
    BROAD_SCALE_STEP = "BROAD_SCALE_STEP"
    LIGHTNESS = "LIGHTNESS"
    SAVE_AS_8BIT = "SAVE_AS_8BIT"
    OUTPUT = 'OUTPUT'

    noise_options = ["no removal", "low", "medium", "high"]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTMstp()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_mstp'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Multi-scale topographic position')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Multi-scale topographic position. "
                       "Calculates Multi-scale topographic position.")

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
                name="LOCAL_SCALE_MIN",
                description="Local scale minimum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="LOCAL_SCALE_MAX",
                description="Local scale maximum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="LOCAL_SCALE_STEP",
                description="Local scale step [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="MESO_SCALE_MIN",
                description="Meso scale minimum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="MESO_SCALE_MAX",
                description="Meso scale maximum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=100,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="MESO_SCALE_STEP",
                description="Meso scale step [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="BROAD_SCALE_MIN",
                description="Broad scale minimum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=100,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="BROAD_SCALE_MAX",
                description="Broad scale maximum radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1000,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="BROAD_SCALE_STEP",
                description="Broad scale step [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=100,
                minValue=1,
                maxValue=1000000000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="LIGHTNESS",
                description="Lightness of image",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.2,
                minValue=0.1,
                maxValue=5.0
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
        local_scale_min = int(self.parameterAsInt(
            parameters,
            self.LOCAL_SCALE_MIN,
            context
        ))
        local_scale_max = int(self.parameterAsInt(
            parameters,
            self.LOCAL_SCALE_MAX,
            context
        ))
        local_scale_step = int(self.parameterAsInt(
            parameters,
            self.LOCAL_SCALE_STEP,
            context
        ))
        meso_scale_min = int(self.parameterAsInt(
            parameters,
            self.MESO_SCALE_MIN,
            context
        ))
        meso_scale_max = int(self.parameterAsInt(
            parameters,
            self.MESO_SCALE_MAX,
            context
        ))
        meso_scale_step = int(self.parameterAsInt(
            parameters,
            self.MESO_SCALE_STEP,
            context
        ))
        broad_scale_min = int(self.parameterAsInt(
            parameters,
            self.BROAD_SCALE_MIN,
            context
        ))
        broad_scale_max = int(self.parameterAsInt(
            parameters,
            self.BROAD_SCALE_MAX,
            context
        ))
        broad_scale_step = int(self.parameterAsInt(
            parameters,
            self.BROAD_SCALE_STEP,
            context
        ))
        lightness = int(self.parameterAsDouble(
            parameters,
            self.LIGHTNESS,
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

        visualization_arr = rvt.vis.mstp(dem=dem_arr,
                                         local_scale=(local_scale_min, local_scale_max, local_scale_step),
                                         meso_scale=(meso_scale_min, meso_scale_max, meso_scale_step),
                                         broad_scale=(broad_scale_min, broad_scale_max, broad_scale_step),
                                         lightness=lightness, ve_factor=ve_factor,
                                         no_data=no_data)
        if not save_8bit:
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_arr, e_type=6, no_data=np.nan)
        else:
            visualization_8bit_arr = rvt.default.DefaultValues().float_to_8bit(
                float_arr=visualization_arr, visualization=RVTVisualization.MULTI_SCALE_TOPOGRAPHIC_POSITION
            )
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_8bit_arr, e_type=1, no_data=np.nan)

        result = {self.OUTPUT: visualization_path}
        return result
