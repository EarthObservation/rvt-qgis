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
import rvt.blend
import rvt.vis
import os


class RVTBlender(QgsProcessingAlgorithm):
    """
    RVT Blender.
    """
    # processing function parameters
    INPUT = 'INPUT'
    BLEND_COMBINATION = 'BLEND_COMBINATION'
    TERRAIN_TYPE = 'TERRAIN_TYPE'
    OUTPUT = 'OUTPUT'
    NOISE_REMOVE = "NOISE_REMOVE"
    SAVE_AS_8BIT = "SAVE_AS_8BIT"

    # read default blender combinations from settings/json, read default terrain settings from settings/json
    default_blender_combinations_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                                     "settings", "default_blender_combinations.json"))
    terrains_settings_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                          "settings", "default_terrains_settings.json"))
    combinations = rvt.blend.BlenderCombinations()
    terrains_settings = rvt.blend.TerrainsSettings()
    combinations.read_from_file(default_blender_combinations_path)
    terrains_settings.read_from_file(terrains_settings_path)

    # find out values for comboboxes
    combinations_names = []
    terrains_sett_names = []
    for combination in combinations.combinations:
        combinations_names.append(combination.name)
    for terrain_sett in terrains_settings.terrains_settings:
        terrains_sett_names.append(terrain_sett.name)

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RVTBlender()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rvt_blender'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RVT Blender')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Relief visualization toolbox, Blender. Calculates blended visualization.")

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
                name="BLEND_COMBINATION",
                description="Combination",
                options=self.combinations_names
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                name="TERRAIN_TYPE",
                description="Terrain type",
                options=self.terrains_sett_names
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
        combination_name = self.combinations_names[int(self.parameterAsEnum(
            parameters,
            self.BLEND_COMBINATION,
            context
        ))]
        terrain_name = self.terrains_sett_names[int(self.parameterAsEnum(
            parameters,
            self.TERRAIN_TYPE,
            context
        ))]
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

        #if save_8bit = True save_float is False, can only output one
        save_float = True
        if save_8bit:
            save_float = False

        # advanced custom combinations (hard coded) blending (which can't be created in dialog)
        if combination_name == "Archaeological combined (VAT combined)":
            vat_combination_json_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                                     "settings", "blender_VAT.json"))
            default_1 = rvt.default.DefaultValues()  # VAT general
            default_2 = rvt.default.DefaultValues()  # VAT flat

            vat_combination_1 = rvt.blend.BlenderCombination()  # VAT general
            vat_combination_2 = rvt.blend.BlenderCombination()  # VAT flat
            vat_combination_1.read_from_file(vat_combination_json_path)
            vat_combination_2.read_from_file(vat_combination_json_path)
            terrain_1 = self.terrains_settings.select_terrain_settings_by_name("general")  # VAT general
            terrain_2 = self.terrains_settings.select_terrain_settings_by_name("flat")  # VAT flat
            terrain_1.apply_terrain(default=default_1, combination=vat_combination_1)  # VAT general
            terrain_2.apply_terrain(default=default_2, combination=vat_combination_2)  # VAT flat

            dict_arr_res_nd = rvt.default.get_raster_arr(raster_path=dem_path)
            vat_combination_1.add_dem_arr(dem_arr=dict_arr_res_nd["array"],
                                          dem_resolution=dict_arr_res_nd["resolution"][0])
            vat_arr_1 = vat_combination_1.render_all_images(default=default_1, no_data=dict_arr_res_nd["no_data"])
            vat_combination_2.add_dem_arr(dem_arr=dict_arr_res_nd["array"],
                                          dem_resolution=dict_arr_res_nd["resolution"][0])
            vat_arr_2 = vat_combination_2.render_all_images(default=default_2, no_data=dict_arr_res_nd["no_data"])

            # blend VAT general and VAT flat together
            combination = rvt.blend.BlenderCombination()
            combination.create_layer(vis_method="VAT general", image=vat_arr_1, normalization="Value", minimum=0,
                                     maximum=1, blend_mode="Normal", opacity=50)
            combination.create_layer(vis_method="VAT flat", image=vat_arr_2, normalization="Value", minimum=0,
                                     maximum=1, blend_mode="Normal", opacity=100)
            combination.add_dem_path(dem_path=dem_path)
            combination.render_all_images(save_render_path=visualization_path, save_visualizations=False,
                                          save_float=save_float, save_8bit=save_8bit,
                                          no_data=no_data)
        elif combination_name == "enhanced Multi-Scale Topographic Position version 3":
            dict_arr_res_nd = rvt.default.get_raster_arr(raster_path=dem_path)
            e3mstp_arr = rvt.blend.e3mstp(dem=dict_arr_res_nd["array"], resolution=dict_arr_res_nd["resolution"][0],
                                          no_data=dict_arr_res_nd["no_data"])
            if save_float:
                rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                        out_raster_arr=e3mstp_arr, no_data=np.nan, e_type=6)
            else:
                rvt.default.save_raster(src_raster_path=dem_path, out_raster_path=visualization_path,
                                        out_raster_arr=rvt.vis.byte_scale(e3mstp_arr, c_min=0.0, c_max=1.0),
                                        no_data=np.nan, e_type=1)
        # normal combination blending
        else:
            # create default
            default = rvt.default.DefaultValues()

            # create combination
            combination = self.combinations.select_combination_by_name(combination_name)
            # apply terrain settings
            terrain_sett = self.terrains_settings.select_terrain_settings_by_name(terrain_name)
            terrain_sett.apply_terrain(default, combination)
            combination.add_dem_arr(dem_arr=dem_arr, dem_resolution=resolution[0])
            combination.add_dem_path(dem_path)
            combination.render_all_images(default=default, save_visualizations=False,
                                          save_render_path=visualization_path,
                                          save_float=save_float, save_8bit=save_8bit, no_data=no_data)

        result = {self.OUTPUT: visualization_path}
        return result
