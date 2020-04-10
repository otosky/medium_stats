import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='medium-stats',
    version='2.1.2',
    entry_points={
        'console_scripts': [
            'medium-stats = medium_stats.__main__:main'
        ]
    },
    packages=find_packages(exclude=("tests",)),
    python_requires='>=3.6',
    install_requires = ['requests', 'lxml'],
    extras_require={
        'selenium': ['selenium', 'webdriver_manager']
    },
    author="Oliver Tosky",
    author_email="olivertosky@gmail.com",
    description="CLI tool to fetch your Medium stats",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="Medium blog scraper analytics",
    license='GNU GPLv3',
    url='https://github.com/otosky/medium_stats'
)