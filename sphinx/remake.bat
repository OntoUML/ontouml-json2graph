echo "01/07: python ..\setup_metadata.py" && ^
python ..\setup_metadata.py && ^
echo "02/07: .\make clean "  && ^
.\make clean && ^
echo "03/07: .\make html" && ^
.\make html && ^
echo "04/07: rmdir ..\docs /s /q" && ^
rmdir ..\docs /s /q && ^
echo "05/07: mkdir ..\docs" && ^
mkdir ..\docs && ^
echo "06/07: xcopy .\_build\html ..\docs\ /E/H" && ^
xcopy .\_build\html ..\docs\ /E/H && ^
echo "07/07: make clean" && ^
make clean