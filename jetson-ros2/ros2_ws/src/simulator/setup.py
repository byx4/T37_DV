from setuptools import setup

package_name = 'simulator'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        # index
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        # pkg files
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', [
            'launch/sim_launch.py',
            'launch/viz.launch.py',
        ]),
    ],
    install_requires=['setuptools', 'PyYAML'],
    zip_safe=True,
    maintainer='bryanx',
    maintainer_email='bryanx@cs.washington.edu',
    description='Merged simulator (core + viz) for T37 DV',
    license='MIT',
    entry_points={
        'console_scripts': [
            # core
            'sim_loop = simulator.sim_loop:main',
            'mimic_perception = simulator.mimic_perception:main',
            'vehicle_dynamics = simulator.vehicle_dynamics:main',
            # viz
            'publish_cone_map = simulator.viz.publish_cone_map:main',
            'pose_to_tf = simulator.viz.pose_to_tf:main',
        ],
    },
)
