from setuptools import setup

package_name = 'controls'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='t37',
    maintainer_email='noreply@example.com',
    description='Shadow controller publishing Ackermann commands',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'controls_node = controls.controls_node:main',
        ],
    },
)
