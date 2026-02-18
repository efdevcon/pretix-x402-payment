from setuptools import setup, find_packages

setup(
    name="pretix-x402-payment",
    version="0.1.0",
    description="x402 crypto payment provider for Pretix — stores and displays on-chain transaction details",
    author="Devcon",
    url="https://github.com/efdevcon/pretix-x402-payment",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=["pretix>=4.16"],
    entry_points="""
[pretix.plugin]
pretix_x402=pretix_x402:PretixPluginMeta
""",
)
