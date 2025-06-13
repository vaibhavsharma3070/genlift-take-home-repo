from setuptools import setup, find_packages

setup(
    name="pattern-extractor",
    version="1.0.0",
    description="Dynamic regex pattern generalization from structured keys",
    author="Vaibhav Sharma",
    author_email="vaibhavsharma3070@gmail.com",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        'dev': ['pytest>=7.0.0', 'pytest-cov>=4.0.0']
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)