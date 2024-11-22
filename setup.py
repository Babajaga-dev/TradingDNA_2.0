"""Setup script for TradingDNA 2.0."""
from setuptools import setup, find_packages

setup(
    name="tradingdna",
    version="2.0.0",
    description="Sistema di Trading Algoritmico Biologico",
    author="TradingDNA Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "rich>=10.0.0",
        "pyyaml>=5.4.0",
        "pytest>=6.2.0",
        "pyarrow>=5.0.0"  # Per file parquet
    ],
    entry_points={
        'console_scripts': [
            'tradingdna=cli.menu:handle_menu',
        ],
    },
    python_requires=">=3.8",
)
