"""
Setup script for KasongoType application
"""

from setuptools import setup, find_packages

setup(
    name="kasongoType",
    version="1.0.0",
    author="KasongoType Team",
    author_email="info@kasongoType.com",
    description="Cyberpunk-themed typing trainer for web and desktop",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kasongoType/kasongoType",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.0.0",
        "PyQt5>=5.15.0",
        "pytest>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "kasongoType-web=web.app:main",
            "kasongoType-desktop=desktop.main:main",
        ],
    },
)