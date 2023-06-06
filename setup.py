import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openmht",
    version="1.0.0",
    author="Jonathan Elliot Perdomo",
    author_email="jonperdomodb@gmail.com",
    description="OpenMHT",
    long_description="An implementation of the multiple hypothesis tracking algorithm for data association.",
    long_description_content_type="text/markdown",
    url="https://github.com/jonperdomo/openmht",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'openmht = openmht.__main__:main'
        ]
    },
)
