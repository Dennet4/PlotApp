@echo off
call clean.bat
python -m build
pip uninstall -y MicroPlotApp
pip install .
rem python -m twine upload dist/*
