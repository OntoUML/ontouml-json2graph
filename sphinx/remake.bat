python ..\setup_metadata.py && .\make clean && .\make html && rmdir ..\docs /s /q && mkdir ..\docs && xcopy .\_build\html ..\docs\ /E/H && make clean
