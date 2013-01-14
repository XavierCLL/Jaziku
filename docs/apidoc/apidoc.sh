#!/bin/bash

cd ../../

sphinx-apidoc2 -o docs/apidoc .

cd docs/apidoc

rm -rf jaziku.data*
rm -rf html

sphinx-build2 . html