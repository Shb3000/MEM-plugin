
from setuptools import setup

setup(
    name="mem-plugin",
    version="1.0.0",
    author="MEM-Plugin Team",
    description="Persistent Memory OS for DeepSeek Harness",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    py_modules=["mem_plugin"],
    install_requires=[
        "numpy>=1.21.0",
        "Pillow>=9.0.0",
        "python-dotenv>=0.19.0",
    ],
    package_data={"*": ["*"]},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    entry_points={"console_scripts": [
        "mem-plugin=mem_plugin:main",
    ]},
)
