#!/bin/bash


cd ../../jaziku

sphinx-apidoc2 -f -d 6 -o ../docs/apidoc .

cd ../docs/apidoc

rm -rf jaziku.data*
rm -rf html

sphinx-build2 . html