from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'orchestrator'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='UWFSAE Driverless Team',
    maintainer_email='uwfsae@example.com',
    description='Central orchestration node for driverless system',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'orchestrator_node = orchestrator.orchestrator_node:main',
        ],
    },
)

