from setuptools import setup

package_name = 'simulator'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name, f'{package_name}.sim_viz'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', [
            'launch/sim_launch.py',
            'launch/viz.launch.py',
            'launch/static_frames.launch.py',
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
            # motion
            'vehicle_dynamics = simulator.vehicle_dynamics:main',
            # perception (fake/local)
            'mimic_perception = simulator.mimic_perception:main',
            # viz
            'publish_cone_map = simulator.sim_viz.publish_cone_map:main',
            'pose_to_tf = simulator.sim_viz.pose_to_tf:main',
        ],
    },
)
