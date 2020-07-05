import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="robinhood-api",
    version="0.0.2",
    author="James Yun",
    author_email="jameswyun99@gmail.com",
    description="the unofficial Robinhood API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/james-yun/robinhood",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests'
    ]
)
