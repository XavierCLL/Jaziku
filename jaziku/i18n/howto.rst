

TRANSLATE
---------

1. generar template "messages.po", go into Jaziku directory and run:

    xgettext jaziku.py plugins/contingency_test.py plugins/globals_vars.py plugins/input_arg.py plugins/input_validation.py plugins/interpolation.py plugins/significance_corr.py plugins/maps/ncl_generator.py plugins/maps/set_grid.py plugins/maps/shapes/Colombia/ncl.py plugins/maps/shapes/Colombia/Colombia/ncl.py

2. move to language (xx) directory: 

    mv messages.po locale/xx/LC_MESSAGES/

3. updated and merge with old if exist (updated olf file based on new file)

    msgmerge jaziku.po messages.po -U

4. translate jaziku.po in localize or your favorite application 

5. compile translated file:

    msgfmt jaziku.po -o jaziku.mo

6. test run Jaziku in other language (or used runfile for this):

    LANG=es jaziku ....
