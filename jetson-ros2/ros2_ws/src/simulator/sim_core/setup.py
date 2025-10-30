from setuptools import setup

package_name = 'sim_core'

setup(
    name=package_name,
    version='0.0.1',
    packages=[
        'sim_core',          # core sim stuff
        'sim_core.sim_viz',  # <- merged viz lives here on disk
    ],
    data_files=[
        # ament index
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),

        # package manifest
        ('share/' + package_name, ['package.xml']),

        # launch files
        ('share/' + package_name + '/launch', [
            'launch/sim_launch.py',
            'launch/viz.launch.py',
            'launch/static_frames.launch.py',
            'launch/sim_rviz.launch.py',   # harmless even if rviz2 not installed
        ]),
    ],
    install_requires=['setuptools', 'PyYAML'],
    zip_safe=True,
    maintainer='bryanx',
    maintainer_email='bryanx@cs.washington.edu',
    description='Minimal simulator core for driverless FSAE (ROS 2 Jazzy), plus visualization helpers.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # core
            'sim_loop = sim_core.sim_loop:main',
            'mimic_perception = sim_core.mimic_perception:main',
            'vehicle_dynamics = sim_core.vehicle_dynamics:main',

            # merged viz (note the path!)
            'publish_cone_map = sim_core.sim_viz.publish_cone_map:main',
            'pose_to_tf = sim_core.sim_viz.pose_to_tf:main',
        ],
    },
)
