from distutils.core import setup

setup(
    name='cotton',
    version='1.1.0',
    packages=['cotton',],
    license='BSD',
    long_description=open('README.markdown').read(),
    install_requires=[
        "fabric",
    ],
)
