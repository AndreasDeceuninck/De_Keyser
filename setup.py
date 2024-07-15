from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="De_Keyser",
    version="0.1.0",
    description="A library for building projects in De Keyser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Andreas Deceuninck",
    author_email="andreas.deceuninck112@gmail.com",
    url="https://github.com/AndreasDeceuninck/De_Keyser/",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy", "datetime", "matplotlib", "pandas"],
    extras_require={
        "dev": ["twine", "pytest"],
    },
    python_requires='>=3.12',
)