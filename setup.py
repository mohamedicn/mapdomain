from setuptools import setup, find_packages

setup(
    name="mapdomain",
    version="1.0.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="A tool for subdomain enumeration and sitemap creation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mohamedicn/mapdomain",
    packages=find_packages(),  
    install_requires=[
        "requests",
        "beautifulsoup4",
        "art",
    ],
    entry_points={
        "console_scripts": [
            "mapdomain=mapdomain.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
