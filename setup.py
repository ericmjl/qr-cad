from setuptools import setup, find_packages

setup(
      # mandatory
      name="qrwifi",
      # mandatory
      version="0.1",
      # mandatory
      author_email="ericmajinglong@gmail.com",
      packages=['qrwifi'],
      package_data={},
      install_requires=['pyqrcode', 'SolidPython', 'numpy', 'Flask', 'click'],
      entry_points={
      	'console_scripts': ['qrwifi = qrwifi.cli:start',
                                'qrapp = qrwifi.app:run',]
      }
)
