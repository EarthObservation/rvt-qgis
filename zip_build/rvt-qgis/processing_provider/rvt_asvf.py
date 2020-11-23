from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterEnum)
from qgis import processing
from numpy import array
import rvt.default
import rvt.vis


class RVTASvf(QgsProcessingAlgorithm):
    """
    RVT Anisotropic Sky-view factor.
    """
    # processing function parameters
    INPUT = 'INPUT'
    VE_FACTOR = 'VE_FACTOR'
    RADIUS = "RADIUS"
    NUM_DIRECTIONS = "NUM_DIRECTIONS"
    NOISE_REMOVE = "NOISE_REMOVE"
    ANISOTROPY_LVL = "ANISOTROPY_LVL"
    ANISOTROPY_DIR = "ANISOTROPY_DIR"
    OUTPUT = 'OUTPUT'

    noise_options = ["no removal", "low", "medium", "high"]
    ani_lvl_options = ["low", "high"]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTASvf()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_asvf'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Anisotropic Sky-view factor')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Anisotropic Sky-view factor. Calculates "
                       "Anisotropic Sky-view factor.")

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
                minValue=0,
                maxValue=10
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
                name="ANISOTROPY_LVL",
                description="Level of anisotropy",
                options=self.ani_lvl_options,
                defaultValue="low"
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="ANISOTROPY_DIR",
                description="Main direction of anisotropy [deg]",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=315,
                minValue=0,
                maxValue=360
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
        asvf_lvl = int(self.parameterAsEnum(
            parameters,
            self.ANISOTROPY_LVL,
            context
        ))
        asvf_lvl += 1
        asvf_dir = float(self.parameterAsDouble(
            parameters,
            self.ANISOTROPY_DIR,
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

        visualization_arr = rvt.vis.sky_view_factor(dem=dem_arr, resolution=resolution[0], compute_svf=False,
                                                    compute_asvf=True, compute_opns=False, svf_n_dir=nr_dir,
                                                    svf_r_max=radius, svf_noise=noise, ve_factor=ve_factor,
                                                    asvf_level=asvf_lvl, asvf_dir=asvf_dir)["asvf"]
        rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                out_raster_arr=visualization_arr, e_type=6)

        result = {self.OUTPUT: visualization_path}
        return result
