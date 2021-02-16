from setuptools import setup, find_packages

setup(
    name='CLI',
    version='3.1.0',
    packages=find_packages(exclude=['test']),
    url='https://github.com/ankit98verma/CLI',
    author='Ankit Verma',
    license='MIT',
    author_email='ankitvermajnp@gmail.com',
    description='CLI interface',
    entry_points={
            'console_scripts': [
                'dds=test.test1:main'
            ]
        },
    install_requires=[
        '',
    ]
)
