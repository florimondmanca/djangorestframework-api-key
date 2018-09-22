"""Package setup."""

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()


setuptools.setup(
    name='djangorestframework-api-key',
    version=__import__('rest_framework_api_key').__version__,
    author='Florimond Manca',
    author_email='florimond.manca@gmail.com',
    description='Web API permissions for the Django REST Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/florimondmanca/djangorestframework-api-key',
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
    ],
)
