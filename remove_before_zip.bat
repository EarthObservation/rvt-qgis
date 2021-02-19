rmdir /s /q .\__pycache__\ 2>nul 

rmdir /s /q .\processing_provider\__pycache__\ 2>nul 

rmdir /s /q .\rvt\__pycache__\ 2>nul 

del ".\settings\plugin_size.json" >nul 2>&1
pause