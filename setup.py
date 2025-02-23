from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        '*',
        ['src/itemcloud/native/*.pyx'],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],        
    )
]
extensions_package_data = {
    'itemcloud.native': [
        '*.pxd',
        '*.pyx'
    ]
}
setup(
    ext_modules=cythonize(extensions),
    package_data = extensions_package_data
)