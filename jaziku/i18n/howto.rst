

TRANSLATE
---------

1. generar template "messages.po", go into Jaziku directory and run:

    find . -iname "*.py" | xargs xgettext --from-code=UTF-8

2. move to language (xx) directory: 

    mv messages.po i18n/xx/LC_MESSAGES/

3. updated and merge with old if exist (updated olf file based on new file)

    msgmerge jaziku.po messages.po -U

4. translate jaziku.po in localize or your favorite application 

5. compile translated file:

    msgfmt jaziku.po -o jaziku.mo

6. test run Jaziku in other language (or used runfile for this):

    LANG=es jaziku ....
