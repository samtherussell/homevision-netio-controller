import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="homevision-netio-controller",
    version="0.1.1",
    author="Jackoson",
    description="A python api for controlling a homevision system via the netio interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackoson/homevision-netio-controller",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)