from setuptools import setup

setup(
    name='DDS',
    version='1.0.5',
    packages=['DDS'],
    url='todo',
    author='Ankit',
    author_email='ankitvermajnp@gmail.com',
    description='CLI interface',
    entry_points={
            'console_scripts': [
                'dds=test.test1:main'
            ]
        }
)
