# Autonomous Vehicle Demo

> **Note:** This demo is temporary and will be deprecated soon. Team members are currently migrating this functionality into the main ROS nodes and packages. This documentation and associated scripts will be removed once the migration is complete.

## Overview

A complete autonomous driving simulation demonstrating cone corridor navigation using ROS 2 Jazzy.

This demo implements a closed-loop autonomous vehicle system that:
1. Simulates a vehicle navigating through a cone corridor
2. Plans an optimal path down the middle of the corridor
3. Controls the vehicle using pure pursuit algorithm

## Architecture

```
┌─────────────┐     /perception/     ┌──────────────┐     /planning/      ┌──────────────┐
│             │──────local_cones────▶│              │────trajectory──────▶│              │
│  simulator  │                      │path_planning │                     │   controls   │
│             │◀─────/controls/──────│              │                     │              │
└─────────────┘      command         └──────────────┘                     └──────────────┘
      │
      │ /state/odom
      ▼
```

### Packages

#### 1. **interfaces** - Message Definitions
Custom ROS messages for the autonomous system:
- `Cone.msg` - Single cone object with position and color
- `ConeArray.msg` - Array of cones with header
- `TrajectoryPoint.msg` - Waypoint with pose and velocity
- `Trajectory.msg` - Complete path trajectory
- `Control.msg` - Vehicle control commands

#### 2. **simulator** - Vehicle Simulator
Physics-based vehicle simulator with environment generation:
- Implements bicycle model dynamics
- Generates simulated cone corridor environment
- Publishes vehicle odometry and TF transforms
- **Topics**:
  - Subscribes: `/controls/command` (Control)
  - Publishes: `/state/odom` (Odometry), `/perception/local_cones` (ConeArray)

#### 3. **path_planning** - Trajectory Planner
Generates drivable paths through the cone corridor:
- Simple midline planner algorithm
- Computes trajectory between left and right cones
- **Topics**:
  - Subscribes: `/perception/local_cones` (ConeArray)
  - Publishes: `/planning/trajectory` (Trajectory)

#### 4. **controls** - Vehicle Controller
Executes planned trajectories using pure pursuit control:
- Pure pursuit path tracking algorithm
- Converts trajectory to steering and speed commands
- **Topics**:
  - Subscribes: `/planning/trajectory` (Trajectory)
  - Publishes: `/controls/command` (Control)

## Quick Start

### Build the Demo

```bash
./scripts/build_av_demo.sh
```

This will:
1. Build the Docker image with all required dependencies
2. Build the ROS 2 packages (interfaces, simulator, path_planning, controls)

### Run the Demo

```bash
./scripts/run_av_demo.sh
```

This launches all three nodes (simulator, planner, controller) in a single process.

You should see output indicating:
- Vehicle simulator starting
- Cone corridor being generated
- Planner receiving cones and publishing trajectories
- Controller tracking the trajectory

### Monitor the Demo

To inspect ROS topics and data:

```bash
./scripts/monitor_av_demo.sh
```

This opens an interactive shell where you can run commands like:
```bash
# List all topics
ros2 topic list

# View cone detections
ros2 topic echo /perception/local_cones

# View planned trajectory
ros2 topic echo /planning/trajectory

# View control commands
ros2 topic echo /controls/command

# View vehicle state
ros2 topic echo /state/odom
```

## Configuration

Each node accepts parameters that can be configured:

### simulator Parameters
- `wheelbase` - Vehicle wheelbase (default: 1.6m)
- `lane_half_width` - Half width of lane (default: 1.5m)
- `cone_spacing` - Distance between cones (default: 3.0m)
- `cones_ahead` - How far ahead to generate cones (default: 25.0m)
- `publish_rate_hz` - Rate for cone publishing (default: 2 Hz)

### controls Parameters
- `lookahead` - Pure pursuit lookahead distance (default: 3.0m)
- `wheelbase` - Vehicle wheelbase (default: 1.6m)

To modify parameters, edit the launch file at:
`ros2_ws/src/orchestrator/launch/simulation.launch.py`

## Manual Operation

If you prefer to run nodes individually:

```bash
# Enter the container
cd docker && docker-compose exec driverless bash

# Source the workspace
source /opt/ros/jazzy/setup.bash
source /workspace/ros2_ws/install/setup.bash

# Run nodes in separate terminals
ros2 run simulator simulator_node
ros2 run path_planning path_planning_node
ros2 run controls controls_node
```

## Troubleshooting

### Build Failures

If the build fails, try rebuilding specific packages:
```bash
cd docker
docker-compose run --rm driverless bash -c "
  source /opt/ros/jazzy/setup.bash && \
  cd /workspace/ros2_ws && \
  colcon build --packages-select interfaces simulator path_planning controls --symlink-install
"
```

### Container Issues

If Docker gives errors, rebuild the image:
```bash
cd docker
docker-compose build --no-cache
```

### Node Communication Issues

Ensure all nodes are using the same ROS_DOMAIN_ID (set to 42 in docker-compose.yml).

Check topic connections:
```bash
ros2 node list
ros2 topic list
ros2 topic info /perception/local_cones
```

## Development

### Adding Features

The packages are mounted from your local filesystem, so you can:
1. Edit code in `ros2_ws/src/`
2. Rebuild inside container: `colcon build --packages-select <package>`
3. Source the workspace: `source install/setup.bash`
4. Test immediately

### Package Structure

```
ros2_ws/src/
├── interfaces/         # Message definitions
├── simulator/          # Simulator + launch files
├── path_planning/      # Path planner
└── controls/           # Controller
```

