from setuptools import setup

package_name = 'path_planning'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='t37',
    maintainer_email='noreply@example.com',
    description='Naive local planner for T37 demo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'path_planning_node = path_planning.path_planning_node:main',
        ],
    },
)
