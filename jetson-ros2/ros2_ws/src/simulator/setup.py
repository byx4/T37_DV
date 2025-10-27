from setuptools import setup

package_name = 'simulator'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/loop_demo.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='t37',
    maintainer_email='noreply@example.com',
    description='Simple bicycle-model simulator for T37 demo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulator_node = simulator.simulator_node:main',
        ],
    },
)
