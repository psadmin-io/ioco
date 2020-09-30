from setuptools import setup, find_packages
from pathlib import Path

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text()
HISTORY = (HERE / "HISTORY.md").read_text()

setup_args = dict(
    name='iocloudops',
    version='0.0.2',
    description='psadmin.io Cloud Operations',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    url='https://github.com/psadmin-io/ioCloudOps',
    
    author='psadmin.io',
    author_email='info@psadmin.io',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        # TODO
    ],
    packages=find_packages(),
    keywords=['PeopleSoft', 'PeopleTools', 'OCI', 'Oracle Cloud Infrastructure', 'Oracle Cloud'],    
    include_package_data=True,
    install_requires=["docopt>=0.6.2","requests","oci"],
    entry_points={
        "console_scripts": [
            "ioco=ioco.__main__:main",
        ]
    },
)

if __name__ == '__main__':
    setup(**setup_args) 
