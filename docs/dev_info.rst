
Guidelines and rules of language syntax
-------------------------

:Pages:
http://epydoc.sourceforge.net/fields.html
http://docutils.sourceforge.net/docs/user/rst/quickref.html
http://epydoc.sourceforge.net/manual-fields.html
http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
http://pythonhosted.org/an_example_pypi_project/sphinx.html

:External code example:
https://github.com/mongodb/mongo-python-driver
https://github.com/ask/celery
https://secure.rhodecode.org/rhodecode/files/tip/

:Example:
.. code-block:: python

    def fetch_bigtable_rows(big_table, keys, other_silly_variable=None, *tools, **options):
        """Fetches rows from a Bigtable.

        Retrieves rows pertaining to the given keys from the Table instance
        represented by big_table.  Silly things may happen if
        other_silly_variable is not None.

        :param big_table: An open Bigtable Table instance.
        :type big_table: int
        :param keys: A sequence of strings representing the key of each table row to fetch.
        :type keys: dict
        :param tools: Tools that should be used to plant the seed.
        :param options: Any extra options for the planting.

        :keyword soak: non-explicit keyword parameters in arguments

        :return: Return a dictionary depend of `class_category_analysis`, thus:

            if `class_category_analysis` is 3:
                - `<dict>`, 2 keys: {'below','above'}
            if `class_category_analysis` is 7:
                - `<dict>`, 6 keys: {'below3','below2','below1','above1','above2','above3'}
        :rtype: dict

        Return by reference:

        :ivar STATION.var_D.data: data read from file
        :ivar STATION.var_D.date: date read from file
        :ivar likes_spam: A boolean indicating if we like SPAM or not.
        :ivar eggs: An integer count of the eggs we have laid.

        :requires: ...

        :examples: examples code here

        .. note:: Requires server version **>= 1.1.3+**

        .. seealso:: :meth:`pymongo.collection.Collection.distinct`

        .. versionadded:: 1.2
        """

        def __init__(self, likes_spam=False):
            """Inits SampleClass with blah."""
            self.likes_spam = likes_spam
            self.eggs = 0

        def public_method(self):
            """Performs operation blah."""
