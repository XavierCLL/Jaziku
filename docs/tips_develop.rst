

TRANSLATE
---------

1. generar template

    xgettext jaziku.py plugins/contingency_test.py plugins/globals_vars.py plugins/input_arg.py plugins/input_validation.py plugins/interpolation.py plugins/significance_corr.py plugins/maps/ncl_generator.py plugins/maps/set_grid.py plugins/maps/shapes/Colombia/ncl.py plugins/maps/shapes/Colombia/Colombia/ncl.py

2. mover a la carpeta del idioma xx: 

    mv messages.po locale/xx/LC_MESSAGES/

3. actualizar y fusionar (actualiza old basado en el nuevo)

    msgmerge jaziku.po messages.po -U

4. treducir en lokalize u otra herramienta el archivo jaziku.po

5. compilar archivo traducido:

    msgfmt jaziku.po -o jaziku.mo

6. alternativa de correrlo con un idioma en particular:

    LANG=es jaziku ....


EGGS AND SOURCE CODE
--------------------

- source code packages

    python2 setup.py sdist

- generar/actualizar egg:

    python2 setup.py bdist_egg

- generar/actualiza exe for windows:

    python2 setup.py bdist_wininst