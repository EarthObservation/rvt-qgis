from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterEnum
                       )
from qgis import processing
import numpy as np
import rvt.default
import rvt.blend
import rvt.vis
import os


class RVTFillNoData(QgsProcessingAlgorithm):
    """
    RVT Fill no data.
    """
    # processing function parameters
    INPUT = 'INPUT'
    METHOD = 'METHOD'
    OUTPUT = 'OUTPUT'

    method_options = ["kd_tree", "nearest_neighbour"]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTFillNoData()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_fill_no_data'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Fill no-data')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Function to fill no data. Note: DEM has to have defined no-data!")

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
            QgsProcessingParameterEnum(
                name="METHOD",
                description="Interpolation method",
                options=self.method_options,
                defaultValue="nearest_neighbour"
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
        method_enum = int(self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        ))
        method = self.method_options[method_enum]
        dem_out_path = (self.parameterAsOutputLayer(
            parameters,
            self.OUTPUT,
            context,
        ))

        dem_path = str(dem_layer.source())

        dict_arr_dem = rvt.default.get_raster_arr(dem_path)
        resolution = dict_arr_dem["resolution"]  # (x_res, y_res)
        dem_arr = dict_arr_dem["array"]
        no_data = dict_arr_dem["no_data"]

        dem_arr[dem_arr == no_data] = np.nan

        dem_out = rvt.vis.fill_where_nan(dem=dem_arr, method=method)
        rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=dem_out_path,
                                out_raster_arr=dem_out, e_type=6, no_data=np.nan)

        result = {self.OUTPUT: dem_out_path}
        return result


class RVTFillNoDataIDW(QgsProcessingAlgorithm):
    """
    RVT Fill no data Inverse Distance Weighting interpolation.
    """
    # processing function parameters
    INPUT = 'INPUT'
    RADIUS = 'RADIUS'
    POWER = 'POWER'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTFillNoDataIDW()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_fill_no_data_idw'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Fill no-data IDW')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Function to fill no data. Note: DEM has to have defined no-data!")

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
                name="RADIUS",
                description="Search radius [pixels]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=20,
                minValue=1,
                maxValue=200
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name="POWER",
                description="Power",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=2,
                minValue=0.2,
                maxValue=10
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
        radius = int(self.parameterAsInt(
            parameters,
            self.RADIUS,
            context
        ))
        power = float(self.parameterAsDouble(
            parameters,
            self.POWER,
            context
        ))
        dem_out_path = (self.parameterAsOutputLayer(
            parameters,
            self.OUTPUT,
            context,
        ))

        dem_path = str(dem_layer.source())

        dict_arr_dem = rvt.default.get_raster_arr(dem_path)
        resolution = dict_arr_dem["resolution"]  # (x_res, y_res)
        dem_arr = dict_arr_dem["array"]
        no_data = dict_arr_dem["no_data"]

        dem_arr[dem_arr == no_data] = np.nan

        dem_out = rvt.vis.fill_where_nan(dem=dem_arr, method=f"idw_{radius}_{power}")
        rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=dem_out_path,
                                out_raster_arr=dem_out, e_type=6, no_data=np.nan)

        result = {self.OUTPUT: dem_out_path}
        return result
