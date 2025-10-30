from setuptools import setup

package_name = 'sim_core'

setup(
    name=package_name,
    version='0.0.1',
    packages=[
        'sim_core',       # your original core stuff
        'sim_core.viz',   # <- this will be the old sim_viz code (see note below)
    ],
    data_files=[
        # ament index
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),

        # package.xml
        ('share/' + package_name, ['package.xml', 'README.md']),

        # launch files (from BOTH old packages)
        ('share/' + package_name + '/launch', [
            'launch/sim_launch.py',       # from old sim_core
            'launch/sim_rviz.launch.py',  # from old sim_core (you can delete later)
            'launch/viz.launch.py',       # from old sim_viz
        ]),
    ],
    install_requires=[
        'setuptools',
        'PyYAML',
    ],
    zip_safe=True,
    maintainer='bryanx',
    maintainer_email='bryanx@cs.washington.edu',
    description='Minimal simulator core for driverless FSAE (ROS 2 Jazzy) with viz helpers.',
    license='MIT AND BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # from old sim_core
            'sim_loop = sim_core.sim_loop:main',
            'mimic_perception = sim_core.mimic_perception:main',
            'vehicle_dynamics = sim_core.vehicle_dynamics:main',

            # from old sim_viz
            'publish_cone_map = sim_core.viz.publish_cone_map:main',
            'pose_to_tf = sim_core.viz.pose_to_tf:main',
        ],
    },
)
