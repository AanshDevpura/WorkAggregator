from setuptools import setup, find_packages

setup(
    name='homework_aggregator',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'psycopg2-binary',
        'pytest',
        'requests',
        'datetime',
        'tzlocal',
        'pytz'
    ],
)