from distutils.core import setup

setup(
    name='cotton',
    version='0.1dev',
    packages=['cotton',],
    license='BSD',
    long_description=open('README.markdown').read(),
    install_requires=[
        "fabric",
    ],
)
