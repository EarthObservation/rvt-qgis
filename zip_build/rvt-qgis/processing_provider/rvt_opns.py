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


class RVTOpns(QgsProcessingAlgorithm):
    """
    RVT Sky-view factor.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    RADIUS = "RADIUS"
    NUM_DIRECTIONS = "NUM_DIRECTIONS"
    NOISE_REMOVE = "NOISE_REMOVE"
    OPNS_TYPE = "OPNS_TYPE"
    SAVE_AS_8BIT = "SAVE_AS_8BIT"
    FILL_NO_DATA = "FILL_NO_DATA"
    KEEP_ORIG_NO_DATA = "KEEP_ORIG_NO_DATA"
    OUTPUT = 'OUTPUT'

    noise_options = ["no removal", "low", "medium", "high"]
    opns_options = ["Positive", "Negative"]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTOpns()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_opns'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Openness')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Openness. Calculates Positive or Negative Openness.")

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
                name="RADIUS",
                description="Search radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10,
                minValue=10,
                maxValue=50
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="NUM_DIRECTIONS",
                description="Number of search directions",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=16,
                minValue=8,
                maxValue=64
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                name="NOISE_REMOVE",
                description="Level of noise removal",
                options=self.noise_options,
                defaultValue="no removal"
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                name="OPNS_TYPE",
                description="Which Openness: Positive or Negative",
                options=self.opns_options,
                defaultValue="Positive"
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
        radius = int(self.parameterAsInt(
            parameters,
            self.RADIUS,
            context
        ))
        nr_dir = int(self.parameterAsInt(
            parameters,
            self.NUM_DIRECTIONS,
            context
        ))
        noise = int(self.parameterAsEnum(
            parameters,
            self.NOISE_REMOVE,
            context
        ))
        opns_type = int(self.parameterAsEnum(
            parameters,
            self.OPNS_TYPE,
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

        vis = "openness - positive"
        if opns_type == 1:
            vis = "openness - negative"
            dem_arr = dem_arr * -1  # negative openness is openness where dem * -1
        visualization_arr = rvt.vis.sky_view_factor(dem=dem_arr, resolution=resolution[0], compute_svf=False,
                                                    compute_asvf=False, compute_opns=True, svf_n_dir=nr_dir,
                                                    svf_r_max=radius, svf_noise=noise, ve_factor=ve_factor,
                                                    no_data=no_data, fill_no_data=fill_no_data,
                                                    keep_original_no_data=keep_orig_no_data)["opns"]
        if not save_8bit:
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_arr, e_type=6, no_data=np.nan)
        else:
            visualization_8bit_arr = rvt.default.DefaultValues().float_to_8bit(float_arr=visualization_arr,
                                                                               vis=vis)
            rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                    out_raster_arr=visualization_8bit_arr, e_type=1, no_data=np.nan)

        result = {self.OUTPUT: visualization_path}
        return result
