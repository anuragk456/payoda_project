from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="firebird-package",
    version="1.0.0",
    author="Anurag kurmi",
    author_email="anurag.k@payoda.com",
    description="A package for managing interview transcripts in Firebird database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/firebird-package",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Add your dependencies here
        # For example: "fdb>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
)