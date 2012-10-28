# vim:fileencoding=utf-8:ai:ts=4:sts:et:sw=4:tw=80:
try:
    from collections import OrderedDict
except ImportError:
    # Py 2.6 compat
    from ordereddict import OrderedDict

from pyramid.settings import asbool
from pyramid.events import ApplicationCreated, BeforeRender
from pyramid.threadlocal import get_current_request

from pyramid_assetcompiler.utils import as_string, as_list
from pyramid_assetcompiler.compiler import Compiler

SETTINGS_PREFIX = 'assetcompiler.'

default_settings = (
    ('debug', asbool, 'false'),
    ('asset_prefix', as_string, '_'),
    ('each_request', asbool, 'true'),
    ('each_boot', asbool, 'false'),
    ('asset_paths', as_list, ('',)),
)

# Use an OrderedDict so that processing always happens in order
compilers = OrderedDict() # empty for now

def parse_settings(settings):
    parsed = {}
    def populate(name, convert, default):
        name = '%s%s' % (SETTINGS_PREFIX, name)
        value = convert(settings.get(name, default))
        parsed[name] = value
    for name, convert, default in default_settings:
        populate(name, convert, default)
    return parsed

def assign_compiler(config, ext, cmd, new_ext):
    """
    Configuration method to set up an asset compiler and its parameters.
    
    :param ext: The file extension to match (e.g. coffee).
    :type ext: string - Required
    
    :param cmd: The command to run (e.g. coffee -c -p). The filename to be
                compiled will automatically be appended to the end of this
                string.
    :type cmd: string - Required
    
    :param new_ext: The extension that the compiled file should have (e.g.
                    js).
    :type new_ext: string - Required
    
    
    .. warning:: The specified compiler command must be installed, must be
                 executable by the Pyramid process, and must *output the
                 compiled data to stdout*. The last point can get tricky
                 depending on the command, so be sure to check its command
                 switches for the appropriate option.
    
    Examples:
    
    A compiler that will compile CoffeeScript files into JavaScript::
    
        config.assign_compiler('coffee', 'coffee -c -p', 'js')
    
    You can even nest compilers. This could allow you to compile CoffeeScript
    files into JavaScript, and then minify the JavaScript (see the docs for
    ``compiled_assetpath``)::
    
        config.assign_compiler('coffee', 'coffee -c -p', 'js')
        config.assign_compiler('js', 'uglifyjs', 'js')
    
    Note: Compilers are first in first out, so make sure you assign accordingly.
    """
    compilers[ext] = dict(cmd=cmd, ext=new_ext)

def compiled_asset_url(path, **kw):
    """
    Returns a Pyramid ``static_url`` url of the compiled asset (and compiles the
    asset if needed).
    
    :param path: The Pyramid asset path to process.
    :type path: string - Required
    
    :type compiler: dict or string - Optional
    :param compiler: Allows you to override/specify a specific compiler to use
                     (e.g. ``coffee``), or assign a brand new compiler
                     dictionary to be used (e.g. ``{'less': {'cmd': 'less',
                     'ext': 'css'}}``)
    """
    request = get_current_request()
    settings = request.registry.settings
    
    compiler = Compiler(settings, path, **kw)
    
    if not settings.get('assetcompiler.each_request'):
        if not compiler.compiled:
            # log an error
            pass
        
        return request.static_url(compiler.new_path)
    else:
        if compiler.compiled:
            return request.static_url(compiler.new_path)
        else:
            return request.static_url(compiler.compile())


def compiled_asset_path(path, **kw):
    """
    Returns a Pyramid ``static_path`` path of the compiled asset (and compiles the
    asset if needed).
    
    :param path: The Pyramid asset path to process.
    :type path: string - Required
    
    :type compiler: dict or string - Optional
    :param compiler: Allows you to override/specify a specific compiler to use
                     (e.g. ``coffee``), or assign a brand new compiler
                     dictionary to be used (e.g. ``{'less': {'cmd': 'less',
                     'ext': 'css'}}``)
    """
    request = get_current_request()
    settings = request.registry.settings
    
    compiler = Compiler(settings, path, **kw)
    
    if not settings.get('assetcompiler.each_request'):
        if not compiler.compiled:
            # log an error
            pass
        
        return request.static_path(compiler.new_path)
    else:
        if compiler.compiled:
            return request.static_path(compiler.new_path)
        else:
            return request.static_path(compiler.compile())

def compiled_asset_source(path, **kw):
    """
    Returns the source data/contents of the compiled asset (and compiles the
    asset if needed). This is useful when you want to output inline data (e.g.
    for inline javascript blocks).
    
    :param path: The Pyramid asset path to process.
    :type path: string - Required
    
    :type compiler: dict or string - Optional
    :param compiler: Allows you to override/specify a specific compiler to use
                     (e.g. ``coffee``), or assign a brand new compiler
                     dictionary to be used (e.g. ``{'less': {'cmd': 'less',
                     'ext': 'css'}}``)
    """
    request = get_current_request()
    settings = request.registry.settings
    
    compiler = Compiler(settings, path, **kw)
    
    if not settings.get('assetcompiler.each_request'):
        if not compiler.compiled:
            # log an error
            return None
        
        return compiler.compiled_data()
    else:
        if compiler.compiled:
            return compiler.compiled_data()
        else:
            compiler.compile()
            return compiler.compiled_data()

def compiled_assetpath(path, **kw):
    """
    Returns a Pyramid ``asset`` path such as ``pkg:static/path/to/file.ext``
    (and compiles the asset if needed).
    
    :param path: The Pyramid asset path to process.
    :type path: string - Required
    
    :type compiler: dict or string - Optional
    :param compiler: Allows you to override/specify a specific compiler to use
                     (e.g. ``coffee``), or assign a brand new compiler
                     dictionary to be used (e.g. ``{'less': {'cmd': 'less',
                     'ext': 'css'}}``)
    
    This function could be used to nest ``pyramid_assetcompiler`` calls (e.g.
    ``compiled_asset_path(compiled_assetpath('pkg:static/js/script.coffee'))``
    could compile a CoffeeScript file into JS, and then further minify the JS
    file) with a compiler configuration such as::
    
        config.assign_compiler('coffee', 'coffee -c -p', 'js')
        config.assign_compiler('js', 'uglifyjs', 'js')
    """
    request = get_current_request()
    settings = request.registry.settings
    
    compiler = Compiler(settings, path, **kw)
    
    if not settings.get('assetcompiler.each_request'):
        if not compiler.compiled:
            # log an error
            pass
        
        return compiler.new_path
    else:
        if compiler.compiled:
            return compiler.new_path
        else:
            return compiler.compile()

def applicationcreated_subscriber(event):
    settings = event.app.registry.settings
    settings['assetcompiler.compilers'] = compilers
    
    if settings.get('assetcompiler.each_boot'):
        asset_paths = settings.get('assetcompiler.asset_paths')
        
        for asset_path in asset_paths:
            compiler = Compiler(settings, asset_path, batch=True)
            compiler.batch_compile()

def beforerender_subscriber(event):
    event['compiled_asset_url'] = compiled_asset_url
    event['compiled_asset_path'] = compiled_asset_path
    event['compiled_asset_source'] = compiled_asset_source
    event['compiled_assetpath'] = compiled_assetpath

def includeme(config):
    """
    Activate the package; usually called via
    ``config.include('pyramid_assetcompiler')`` instead of being invoked
    directly.
    """
    settings = parse_settings(config.registry.settings)
    config.registry.settings.update(settings)
    
    config.add_directive('assign_compiler', assign_compiler)
    config.add_subscriber(applicationcreated_subscriber, ApplicationCreated)
    config.add_subscriber(beforerender_subscriber, BeforeRender)
