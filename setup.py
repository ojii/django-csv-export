from setuptools import setup, find_packages

version = __import__('csvexport').__version__

setup(
    name = 'django-csv-export',
    version = version,
    description = 'Django CSV Export',
    author = 'Jonas Obrist',
    url = 'http://github.com/ojii/django-csv-export',
    packages = find_packages(),
    zip_safe=False,
    package_data={
        'csvexport': [
            'templates/csvexport/*.html',
        ],
    },
)