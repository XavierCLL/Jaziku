#!/bin/bash

function all() {

    clean

    cd ../../jaziku

    sphinx-apidoc2 -f -o ../docs/apidoc .

    cd ../docs/apidoc

    rm -rf jaziku.data*

    sphinx-build2 -b html . html
}

function clean() {
    rm -rf html
    rm -rf _build
    #find . | grep -vE '(conf.py|index.rst|build.sh|Makefile|make.bat)' | xargs rm
    find . -type f ! -regex ".*/\(conf.py\|index.rst\|build.sh\|Makefile\|make.bat\)" -delete
    
}

case "$1" in
    all)
        all
        ;;
    clean)
        clean
        ;;
    *)
        echo $"Usage: $0 {all|clean}"
        RETVAL=3
        ;;
esac