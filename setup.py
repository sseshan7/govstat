from setuptools import setup

setup(
    name="govstat",
    version="0.0.1",
    author="stevesdawg",
    long_description="",
    description="",
    zip_safe=False,
    packages=["app"],
    install_requires=[
        "beautifulsoup4",
        "cryptography",
        "flask",
        "flask_migrate",
        "flask_sqlalchemy",
        "flask_wtf",
        "gunicorn",
        "numpy",
        "openpyxl",
        "pandas",
        "pymysql",
        "requests",
        "united_states_congress",
        "xlrd",
    ],
    extras_require={
        "dev": ["pre-commit"],
    },
)
