from setuptools import setup, find_packages

setup(
    name='medium-stats',
    version='1.0',
    entry_points={
        'console_scripts': [
            'medium-stats = medium_stats.__main__:main'
        ]
    },
    packages=find_packages(),
    install_requires = ['requests'],
    extras_require={
        'selenium': ['selenium', 'webdriver_manager']
    },
    author="Oliver Tosky",
    author_email="olivertosky@gmail.com",
    description="CLI tool to fetch your Medium stats",
    keywords="Medium blog scraper analytics",
    license='GNU GPLv3'
)