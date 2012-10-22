import os, sys
from setuptools import setup, find_packages

requires = [
    'pyramid>=1.3dev',
]

if sys.version_info[:2] < (2, 7):
    requires.append('ordereddict')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except IOError:
    README = ''
    CHANGES = ''

setup(
    name='pyramid_assetcompiler',
    version='0.1',
    author='Seth Davis',
    author_email='seth@curiasolutions.com',
    description="Dynamic asset compiling for Pyramid. Easily adds support " + \
                "for popular asset metalanguages such as CoffeeScript, " + \
                "SASS, SCSS, LESS, Dart, TypeScript, etc.",
    long_description=README + '\n\n' + CHANGES,
    url='http://github.com/seedifferently/pyramid_assetcompiler',
    keywords='pyramid assets coffeescript sass scss less dart typescript css3',
    packages=find_packages(),
    install_requires=requires,
    tests_require=requires,
    license = "MIT",
    platforms = "Posix; MacOS X; Windows",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Framework :: Pylons',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ]
)
