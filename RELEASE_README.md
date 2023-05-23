# Release of QGIS Plugin for Relief Visualization Toolbox

Here is a guide how to upload (release) new version of the RVT QGIS plugin to the QGIS plugin repository.

Required is pb_tool python library (pip install pb_tool) and 
Qt Creator software to change version in about dialogue (can also be done with txt editor).

To release/upload changes (new version):
*   Change version in `metadata.txt`.
*   Open file `qrvt_dialog_about.ui` (about dialogue) with Qt Creator and change version.
*   Run `remove_before_zip.bat` to remove all pycache files.
*   Create new zip release file with pb_tool plugin: run `pbt zip` in root project directory (`rvt-qgis`). 
    Newly created zip file `rvt-qgis.zip` will be created/overwritten in `zip_build` subdirectory.
*   Login to QGIS plugin repository (https://plugins.qgis.org/plugins/) then click `Upload a plugin` 
    and upload newly created `rvt-qgis.zip` file.
*   Add changes to plugin changelog in `RVT_py` repository, file `qgis_releases.rst`.