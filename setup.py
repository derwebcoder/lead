from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='lead',
    version='1.0.0',
    description='Building and running pipelines using Docker.',
    long_description=readme,
    author='Marvin Becker',
    author_email='marvinbecker@derwebcoder.de',
    url='https://github.com/derwebcoder/lead',
    license=license,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'lead = lead.core:init'
        ]
    },
    install_requires=[
        'docker==2.3.0'
    ]
)