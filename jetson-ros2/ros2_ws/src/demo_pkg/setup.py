from setuptools import find_packages, setup

package_name = 'demo_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'demo_orchestrator_node = demo_pkg.demo_orchestrator_node:main',
            'demo_perception_node = demo_pkg.demo_perception_node:main',
            'demo_planning_node = demo_pkg.demo_planning_node:main',
            'demo_control_node = demo_pkg.demo_control_node:main',
        ],
    },
)
