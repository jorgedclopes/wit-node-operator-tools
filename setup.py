import setuptools
import setup_server

setuptools.setup(
    name='wit-node-operator-tools',
    version=setup_server.version,
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
