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


class RVTSim(QgsProcessingAlgorithm):
    """
    RVT Sky illumination.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    SKY_MODEL = "SKY_MODEL"
    NUM_DIRECTIONS = "NUM_DIRECTIONS"
    SHADOW_DIST = "SHADOW_DIST"
    SHADOW_AZIMUTH = "SHADOW_AZIMUTH"
    SHADOW_ELEVATION = "SHADOW_ELEVATION"
    SAVE_AS_8BIT = "SAVE_AS_8BIT"
    OUTPUT = 'OUTPUT'

    sky_model_options = ["overcast", "uniform"]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTSim()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_sim'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Sky illumination')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Sky illumination. Calculates Sky illumination.")

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
            QgsProcessingParameterEnum(
                name="SKY_MODEL",
                description="Sky model",
                options=self.sky_model_options,
                defaultValue="overcast"
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="NUM_DIRECTIONS",
                description="Number of horizon search directions",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=32,
                minValue=8,
                maxValue=128
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="SHADOW_DIST",
                description="Max shadow modeling distance",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=100,
                minValue=10,
                maxValue=1000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="SHADOW_AZIMUTH",
                description="Shadow azimuth",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=315,
                minValue=0,
                maxValue=360
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="SHADOW_ELEVATION",
                description="Shadow elevation",
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
        sky_model_enum = int(self.parameterAsEnum(
            parameters,
            self.SKY_MODEL,
            context
        ))
        sky_model = self.sky_model_options[sky_model_enum]
        nr_dir = int(self.parameterAsInt(
            parameters,
            self.NUM_DIRECTIONS,
            context
        ))
        max_fine_rad = float(self.parameterAsInt(
            parameters,
            self.SHADOW_DIST,
            context
        ))
        shadow_az = float(self.parameterAsDouble(
            parameters,
            self.SHADOW_AZIMUTH,
            context
        ))
        shadow_el = float(self.parameterAsDouble(
            parameters,
            self.SHADOW_ELEVATION,
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

        visualization_arr = rvt.vis.sky_illumination(dem=dem_arr, resolution=resolution[0], sky_model=sky_model,
                                                     max_fine_radius=max_fine_rad, num_directions=nr_dir,
                                                     ve_factor=ve_factor,
                                                     compute_shadow=True, shadow_az=shadow_az, shadow_el=shadow_el,
                                                     no_data=no_data)
        if not save_8bit:
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_arr, e_type=6, no_data=np.nan)
        else:
            visualization_8bit_arr = rvt.default.DefaultValues().float_to_8bit(float_arr=visualization_arr,
                                                                               vis="sky illumination")
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_8bit_arr, e_type=1, no_data=np.nan)

        result = {self.OUTPUT: visualization_path}
        return result
