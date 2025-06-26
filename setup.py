from setuptools import setup, find_packages

setup(
    name="compliance_framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "typing-extensions>=4.0.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "pytest11": [
            "compliance = compliance_framework.plugin"
        ]
    }
)
