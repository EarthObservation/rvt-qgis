.. _usage:

Usage
=====

#. Open a DEM file to be visualized.

   .. image:: ./figures/rvt_qgis_dem.png

#. Select ``Raster → Relief Visualization Toolbox``.

   .. image:: ./figures/rvt_qgis_menu.png

Usage Visualizations
====================

#. Chose DEM in ``List of currently selected files:``, then choose Visualizations tab. In Visualization tab select preferred visualizations and set their parameters (options).

   .. image:: ./figures/rvt_qgis_toolbox.png

#. Click ``Start`` to calculate visualizations.

The visualizations are stored as GeoTIFFs in the same folder as the input file or to custom location (if ``Save to raster location`` check box is unchecked and directory is set in the line edit next to it).
Visualizations are also added to QGIS main window if ``Add to QGIS`` check box is checked. If ``Overwrite`` check box is checked program overwrites specific visualization file in case it already exists.

   .. image:: ./figures/rvt_qgis_svf.png

The visualizations are described in the `Relief Visualization Toolbox in Python documentation <https://rvt-py.readthedocs.io>`_.

Usage Blender
=============

#. Chose DEM in ``List of currently selected files:``, then choose Blender tab. In Blender tab select your ``Blend combination:`` or build your own in layers.

You can add to list your own custom combination by inputting its name in ``Combination name`` line edit and clicking ``Add``. To remove it just select it (``Blend combination`` list) and click ``Remove``.
It is also possible to save your combination to JSON file (to send it to someone or store it), to do that input its name (``Combination name`` line edit) and click ``Save ...`` (select file location and name).
Saved JSON combinations can be added by clicking ``Load ...`` button (select file). For each visualization method used in blend combination you can change parameters in Visualizations tab.
If you check ``Use preset values for terrain type`` it applies selected terrain type (changes layers min, max and visualizations parameters). If you check ``Save visualizations`` all the visualization used in blender combination will be saved.

   .. image:: ./figures/rvt_qgis_blender.png

#. Click ``Blend images`` to calculate blended image.

   .. image:: ./figures/rvt_qgis_vat.png

Blended image is stored as GeoTIFF in the same folder as the input file or to custom location (if ``Save to raster location`` check box is unchecked and directory is set in the line edit next to it).

Usage Processing functions
==========================

#. In QGIS go to ``Processing Toolbox → Relief visualization toolbox`` there you have all the Relief Visualization Toolbox visualization functions and you can use them.

   .. image:: ./figures/rvt_qgis_processing_toolbox.png