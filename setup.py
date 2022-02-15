from setuptools import setup

setup(
    name='govstat',
    version='0.0.1',
    author='stevesdawg',
    long_description='',
    description='',
    zip_safe=False,
    packages=['app'],
    install_requires=[
        "flask",
        "flask_migrate",
        "flask_sqlalchemy",
        "flask_wtf",
        "numpy",
        "pandas",
        "pymysql",
        "requests",
        "xlrd",
    ],
    entry_points={
        'console_scripts': [
            'govstat = app',
        ],
    },
)
