from distutils.core import setup


setup(
    name='django-director',
    version='0.1.3',
    packages=[
        'director',
    ],
    license='MIT',
    long_description=open('pypi.rst').read(),
    description=('Run manage.py commands in the '
                 'background and collect artefacts.'),
    author="Anentropic",
    author_email="ego@anentropic.com",
    url="https://github.com/anentropic/django-director",
    install_requires=[
        "django-jsonfield >= 0.9",
    ],
)
