
Syntax language and rules
-------------------------

:Pages:
http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
http://pythonhosted.org/an_example_pypi_project/sphinx.html

:External code example:
https://github.com/mongodb/mongo-python-driver
https://github.com/ask/celery
https://secure.rhodecode.org/rhodecode/files/tip/

:Example:
.. code-block:: python

    def fetch_bigtable_rows(big_table, keys, other_silly_variable=None):
        """Fetches rows from a Bigtable.

        Retrieves rows pertaining to the given keys from the Table instance
        represented by big_table.  Silly things may happen if
        other_silly_variable is not None.

        :Args:
            - `big_table`: An open Bigtable Table instance.
            - `keys`: A sequence of strings representing the key of each table row
                to fetch.
            - `other_silly_variable`: Another optional variable, that has a much
                longer name than the other args, and which does nothing.

        :Returns:
            A dict mapping keys to the corresponding table row data
            fetched. Each row is represented as a tuple of strings. For
            example:

            {'Serak': ('Rigel VII', 'Preparer'),
             'Zim': ('Irk', 'Invader'),
             'Lrrr': ('Omicron Persei 8', 'Emperor')}

            If a key from the keys argument is missing from the dictionary,
            then that row was not found in the table.

        :Attributes:
            - `likes_spam`: A boolean indicating if we like SPAM or not.
            - `eggs`: An integer count of the eggs we have laid.

        Examples:
            examples code here

        :Raises:
            - `IOError`: An error occurred accessing the bigtable.Table object.

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
