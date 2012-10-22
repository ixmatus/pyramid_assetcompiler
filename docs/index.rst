pyramid_assetcompiler
=====================

Overview
--------

:mod:`pyramid_assetcompiler` provides automatic asset compiling for your Pyramid
applications.

.. warning:: This package only supports Pyramid 1.3 and later.

Installation
------------

To install, simply::

    pip install pyramid_assetcompiler

* You'll need to have `Python`_ 2.6+ and `pip`_ installed.

.. _Python: http://www.python.org
.. _pip: http://www.pip-installer.org


Setup
-----

Once :mod:`pyramid_assetcompiler` is installed, you must use the
``config.include`` mechanism to include it into your Pyramid project's
configuration.  In your Pyramid project's ``__init__.py``:

.. code-block:: python

    config = Configurator(...)
    config.include('pyramid_assetcompiler')

Alternately, instead of using the Configurator's ``include`` method, you can
activate the add-on by modifying your application's ``.ini`` file, using the
following line:

.. code-block:: ini

    pyramid.includes = pyramid_assetcompiler

Once you've included ``pyramid_assetcompiler``, you must assign one or more
*compilers* via the :meth:`~pyramid_assetcompiler.assign_compiler` configuator
method so that it will know what assets you want compiled. The configuration
method syntax is::

    config.assign_compiler('CURRENT_EXTENSION', 'COMMAND', 'NEW_EXTENSION')

For example, this code would initialize compilers for CoffeeScript and LESS
files:

.. code-block:: python

    config = Configurator(...)
    config.include('pyramid_assetcompiler')
    config.assign_compiler('coffee', 'coffee -c -p', 'js')
    config.assign_compiler('less', 'lessc', 'css')


Usage
-----

Once you have assigned your compilers, you can use one of the view helper
methods combined with Pyramid's asset path syntax to check and (if needed)
compile an asset.

Three view helper methods are provided depending on your desired results:

    .. automodule:: pyramid_assetcompiler
        :noindex:

    .. autofunction:: compiled_asset_url
        :noindex:

    .. autofunction:: compiled_asset_path
        :noindex:

    .. autofunction:: compiled_assetpath
        :noindex:

An example using the Chameleon_ template language:

.. code-block:: xml

    <script src="${compiled_asset_url('pkg:static/js/test.coffee')}"
            type="text/javascript"></script>

:meth:`~pyramid_assetcompiler.compiled_assetpath` is a particularly nifty/dirty
method which gives you the ability to chain compilers. For example, if you
wanted to compile a CoffeeScript file into a JavaScript file and then minify
the JavaScript file you could do something like:

.. code-block:: xml

    <script src="${compiled_asset_url(compiled_assetpath('pkg:static/js/test.coffee')}"
            type="text/javascript">
    </script>

.. _Chameleon: http://chameleon.repoze.org/


Compilers
---------

You can assign as many compilers as you would like using the configurator
method, but it is important to keep in mind the following:

    * The compiler ``COMMAND`` must be installed, must be executable by the
      Pyramid process, and must *output the compiled data to stdout*. The last
      point can get tricky depending on the command, so be sure to check its
      command switches for the appropriate option.
    * Compilers are executed in order, which means that it is possible to
      compile a CoffeeScript file into a JavaScript file and then minify the
      JavaScript file--but only if you have assigned the CoffeeScript compiler
      before the JavaScript compiler.

Here are a few compilers that have been tested and are known to work as of this
writing:

.. code-block:: python

    config.assign_compiler('coffee', 'coffee -c -p', 'js')
    config.assign_compiler('dart', 'dart2js', 'js')
    config.assign_compiler('less', 'lessc', 'css')
    config.assign_compiler('sass', 'sass', 'css')
    config.assign_compiler('scss', 'sass --scss', 'css')
    config.assign_compiler('js', 'uglifyjs', 'js')

Settings
--------

Additional settings are configurable via your Pyramid application's ``.ini``
file (in the app section representing your Pyramid app) using the
``assetcompiler`` key:

    ``assetcompiler.asset_prefix``
        *Default: _*
        
        A prefix to add to the compiled asset filename. Some "directory" forms
        may even be supported (e.g. "``../cache/_``").

    ``assetcompiler.each_request``
        *Default: true*
        
        Whether or not assets should be checked/compiled during each request
        when the template language encounters one of the ``compile_asset*``
        methods.

    ``assetcompiler.each_boot``
        *Default: false*
        
        Whether or not assets should be checked/compiled when the application
        boots (uses the ``pyramid.events.ApplicationCreated`` event).
        
        .. note:: If set to true, then you must specify the ``asset_paths`` to
                  be checked (see below).

    ``assetcompiler.asset_paths``
        *Default: [empty]*
        
        Which path(s) should be checked/compiled when the application boots
        (only loaded if ``assetcompiler.each_boot`` is set to true).
        
        .. note:: Asset path checks are not recursive, so you must explicitly
                  specify each path that you want checked.

For example, if you only wanted to check/compile assets on each boot, and only
wanted to process the ``js`` and ``css`` directories, and would like each
compiled ``_filename`` to be saved in a ``mypackage:static/cached`` directory,
then your ``.ini`` file could look something like:

.. code-block:: ini

    [app:myapp]
    .. other settings ..
    pyramid.includes = pyramid_assetcompiler
    assetcompiler.prefix = ../cache/_
    assetcompiler.each_request = false
    assetcompiler.each_boot = true
    assetcompiler.asset_paths = 
        mypackage:static/js
        mypackage:static/css


Logging
-------

``pyramid_assetcompiler`` uses the logger named ``pyramid_assetcompiler``. It
sends output at a DEBUG level useful for its own developers to see what's
happening.


More Information
----------------

.. toctree::
   :maxdepth: 1

   api.rst


Development Versions / Reporting Issues
---------------------------------------

Visit http://github.com/seedifferently/pyramid_assetcompiler to download
development or tagged versions.

Visit http://github.com/seedifferently/pyramid_assetcompiler/issues to report
issues.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
