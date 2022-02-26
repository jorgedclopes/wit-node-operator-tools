import setuptools
import prometheus_wit_client

setuptools.setup(
    name='wit-node-operator-tools',
    version=prometheus_wit_client.version,
    packages=setuptools.find_packages(),
    url='',
    license='',
    maintainer='Jorge Lopes',
    maintainer_email='jorgedclopes@gmail.com',
    author='Jorge Lopes',
    author_email='jorgedclopes@gmail.com',
    description='Assorted scripts to setup and operate on Witnet Nodes.',
    include_package_data=True
)
