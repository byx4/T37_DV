# UWFSAE Jetson ROS2 Stack

Driverless Formula Student autonomous stack running ROS 2 Jazzy on NVIDIA Jetson Orin AGX.

## Overview

This repository provides a Docker-based development workflow for building and testing driverless vehicle software. The same codebase runs on both local development machines and the NVIDIA Jetson Orin AGX deployment target.

**Key Features:**
- Containerized development with Docker 🐳
- ROS 2 Jazzy with pre-configured environment
- Identical environments across development and deployment

## Available Demos

This repository includes two complete autonomous system demonstrations:

1. **Basic Demo** (`demo_pkg`) - Template orchestrator-based system
2. **Autonomous Vehicle Demo** *(deprecated, will be removed soon)* - Complete cone corridor navigation simulation with physics-based vehicle model, path planning, and pure pursuit control. Team members are migrating this functionality into the main ROS packages.

**New to the project?** → See [**docs/SETUP.md**](docs/SETUP.md) for complete setup instructions.

**Want to run the autonomous vehicle demo?** → See [**docs/DEMO.md**](docs/DEMO.md)

## Getting Started

**Quick reference:**
```bash
# Build container
cd docker && docker build -t jetson-ros2:latest -f Dockerfile ..

# Start container (development machines)
docker-compose up -d

# Enter container
docker-compose exec driverless bash

# Build workspace (inside container)
cd /workspace/ros2_ws && colcon build && source install/setup.bash

# For Jetson with GPU:
# docker-compose -f docker-compose.yml -f docker-compose.jetson.yml up -d
```

## Project Structure
```
jetson-ros2/
├── docker/                    # Docker configuration
│   ├── Dockerfile             # ROS 2 Jazzy container
│   └── docker-compose.yml     # Compose configuration
├── ros2_ws/                   # ROS 2 workspace
│   ├── src/
│   │   ├── orchestrator/      # Central orchestration & system-wide launch files
│   │   ├── demo_pkg/          # Basic demo package
│   │   ├── interfaces/        # Custom message definitions
│   │   ├── lidar_driver/      # LiDAR sensor interface
│   │   ├── perception/        # Cone detection pipeline
│   │   ├── simulator/         # Vehicle simulator
│   │   ├── path_planning/     # Path planner
│   │   └── controls/          # Controller
│   ├── build/                 # Build artifacts (gitignored)
│   ├── install/               # Install space (gitignored)
│   └── log/                   # Build logs (gitignored)
├── docs/                      # Documentation
│   ├── SETUP.md               # Setup instructions
│   ├── DEMO.md                # Demo guide
│   └── PERCEPTION_INTEGRATION.md  # Perception integration guide
├── scripts/                   # Utility scripts
│   ├── build_av_demo.sh       # Build AV demo
│   ├── run_av_demo.sh         # Run AV demo
│   └── monitor_av_demo.sh     # Monitor AV demo
└── README.md                  # This file
```

## System Architecture

The autonomous system follows a standard robotics pipeline:

```
┌──────────────┐  /perception/lidar_data    ┌────────────┐  /perception/local_cones
│ lidar_driver │ ─────────────────────────> │ perception │ ───────────────────────┐
└──────────────┘     (PointCloud2)          └────────────┘     (ConeArray)        │
                                                                                  │
                                                                                  ▼
┌──────────┐   /controls/command  ┌───────────────┐   /planning/trajectory  ┌─────────────┐
│ controls │ <─────────────────── │ path_planning │ <────────────────────── │ (simulator) │
└──────────┘      (Control)       └───────────────┘      (Trajectory)       └─────────────┘
```

**Active Packages:**
- `orchestrator` - Central system orchestration and mission management (*in development*)
- `lidar_driver` - Ouster LiDAR interface (skeleton)
- `perception` - Cone detection from LiDAR (skeleton)
- `simulator` - Vehicle physics and cone simulation
- `path_planning` - Midline trajectory generation
- `controls` - Pure pursuit controller
- `interfaces` - Shared message definitions

**Legacy Demo Package:**
- `demo_pkg` - Template orchestrator-based system (reference implementation)

All nodes communicate via ROS 2 topics and follow the Jazzy API.

### Orchestrator Package

The `orchestrator` package is the **central coordination point** of the driverless system. It serves as the top-level controller responsible for:

- System-level setup and configuration
- Tracking the current autonomous mission (e.g., ACCELERATION, SKIDPAD, AUTOCROSS, TRACKDRIVE)
- Managing lifecycle of system components
- Integrating with the CAN bus for mission selection and control signals

**Current Status:** The orchestrator node is currently a placeholder under active development. It maintains mission state internally but does not yet interact with other system components. Future development will add CAN message integration and dynamic node lifecycle management.

**System-Wide Launch Files:** All launch files that boot up multi-package system configurations (e.g., the full car stack or simulation stack) are located in `orchestrator/launch/`. This centralizes system-level configuration and separates it from package-specific test launch files.

Individual packages may have their own launch files for smaller-scale testing (e.g., testing perception with lidar_driver only, or controls with path_planning). System-wide integration launch files should only be placed in the orchestrator package.

## Development Workflow

1. **Edit code** on your local machine in `ros2_ws/src/`
2. **Rebuild** inside container: `colcon build --packages-select <pkg>`
3. **Test immediately** - changes are live via volume mounting

## Docker Environment

The same Dockerfile builds identical environments for development and Jetson deployment - same OS, ROS 2, Python, and dependencies. On Jetson, we add GPU runtime and hardware access via an override file.

**Development (Mac/Windows/Linux):**
```bash
cd docker
docker-compose up -d
docker-compose exec driverless bash
```

**Jetson (adds GPU/hardware):**
```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.jetson.yml up -d
docker-compose exec driverless bash
```

Use `docker-compose` to manage containers - it allows multiple terminals to enter the same container, essential for running multiple nodes.

See [docs/SETUP.md](docs/SETUP.md) for complete instructions.
