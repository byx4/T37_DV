# UWFSAE Jetson ROS2 Stack - Setup Guide

Complete setup instructions for running the jetson-ros2 stack on your local machine.

---

## Prerequisites

### Required Software
- **Git** - for version control
- **Docker Desktop** - for containerized development
- **Text Editor/IDE** - VS Code, Cursor, or similar

### System Requirements
- **macOS**: M-series (ARM64) or Intel (x86_64)
- **Windows**: WSL2 with Ubuntu
- **Linux**: Ubuntu 20.04+ recommended

---

## Initial Setup

### 1. Install Docker Desktop

**macOS:**
```bash
# Option 1: Homebrew
brew install --cask docker

# Option 2: Download from website
# Visit: https://www.docker.com/products/docker-desktop
# Choose: Mac with Apple Silicon OR Mac with Intel chip
```

**Windows:**
1. Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
2. Download Docker Desktop: https://www.docker.com/products/docker-desktop
3. Enable WSL2 backend in Docker settings

**Linux:**
```bash
# Follow official instructions
# https://docs.docker.com/engine/install/ubuntu/
```

**Verify Installation:**
```bash
docker --version
# Should show: Docker version 24.x.x or higher
```

### 2. Clone the Repository
```bash
# Navigate to your projects directory
cd ~/Documents  # or wherever you keep projects

# Clone the repository
git clone git@github.com:uwfsae/jetson-ros2.git

# Navigate into it
cd jetson-ros2
```

---

## Building the Docker Container

### First Time Build (<10mins)
The first build installs ROS 2 Jazzy and all dependencies.

```bash
# Navigate to docker directory
cd docker

# Build the image
docker build -t jetson-ros2:latest -f Dockerfile ..

# Wait for build to complete...
```

**Note:** This only needs to be done once per machine. Subsequent builds (when adding dependencies) will be much faster due to Docker layer caching.

---

## Running the Demo Package

### Starting the Container

**Using docker-compose (Recommended):**

Docker Compose is recommended because it manages container configuration in files and allows multiple terminals to enter the same running container, which is essential for running multiple ROS nodes.

**Development (macOS/Windows/Linux):**
```bash
cd docker
docker-compose up -d
docker-compose exec driverless bash
```

**Jetson (with GPU support):**
```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.jetson.yml up -d
docker-compose exec driverless bash
```

**Alternative - Using docker run:**

You can also use `docker run` directly, but you'll need to recreate containers for each terminal:
```bash
cd docker
docker run -it --rm -v $(pwd)/../ros2_ws:/workspace/ros2_ws jetson-ros2:latest
```

### Building the Workspace
```bash
# Inside the container
cd /workspace/ros2_ws

# Build all packages
colcon build

# Source the workspace
source install/setup.bash
```

### Running Individual Nodes
```bash
# Run orchestrator
ros2 run demo_pkg demo_orchestrator_node

# Run perception (in a new terminal - see below)
ros2 run demo_pkg demo_perception_node

# Run planning
ros2 run demo_pkg demo_planning_node

# Run control
ros2 run demo_pkg demo_control_node
```

### Running Multiple Nodes Simultaneously

Start the container once, then open multiple terminals and run nodes in each:

```bash
# Terminal 1
cd docker && docker-compose exec driverless bash
cd /workspace/ros2_ws && source install/setup.bash
ros2 run demo_pkg demo_orchestrator_node

# Terminal 2
cd docker && docker-compose exec driverless bash
cd /workspace/ros2_ws && source install/setup.bash
ros2 run demo_pkg demo_perception_node

# Terminal 3, 4, etc. - same pattern
```

**Note:** Use `docker-compose exec` to enter the same running container, not `docker run` which creates separate containers.

---

## Development Workflow

### Making Code Changes

1. Edit code on your local machine using your preferred IDE
2. Rebuild inside the container:
   ```bash
   cd /workspace/ros2_ws
   colcon build --packages-select demo_pkg
   source install/setup.bash
   ```
3. Test the changes by running nodes

### Adding New Nodes

1. Create the Python file in `ros2_ws/src/demo_pkg/demo_pkg/`
2. Make it executable: `chmod +x new_node.py`
3. Add entry point to `setup.py`:
   ```python
   entry_points={
       'console_scripts': [
           'new_node = demo_pkg.new_node:main',
       ],
   },
   ```
4. Rebuild: `colcon build --packages-select demo_pkg`

### Adding Dependencies

1. Edit `docker/Dockerfile` (lines 40-58)
2. Add packages:
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends \
       python3-opencv \
       python3-numpy \
       && rm -rf /var/lib/apt/lists/*
   ```
3. Rebuild:
   ```bash
   cd docker
   docker-compose build
   docker-compose down && docker-compose up -d
   ```
4. Commit changes to git

---

## Troubleshooting

### Docker Permission Denied (Linux)
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Container Can't Find ROS
```bash
# Make sure ROS is sourced
source /opt/ros/jazzy/setup.bash
echo $ROS_DISTRO  # Should show "jazzy"
```

### Workspace Build Fails
```bash
# Clean and rebuild
cd /workspace/ros2_ws
rm -rf build install log
colcon build
```

### Volume Mount Not Working

- Verify the path in the docker run command matches your repository location
- Use full path instead of relative: `-v /full/path/to/ros2_ws:/workspace/ros2_ws`

### Can't See Code Changes in Container

- Make sure you're mounting the volume: `-v ...`
- Rebuild after changes: `colcon build`
- Re-source: `source install/setup.bash`

---

## Useful Commands
```bash
# List running containers
docker ps

# Stop a container
docker stop <CONTAINER_ID>

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# View ROS topics
ros2 topic list

# View ROS nodes
ros2 node list

# Echo a topic
ros2 topic echo /topic_name
```

---

## Jetson Deployment

The same Docker image and workflow are used on Jetson - the environment is identical. The only difference is enabling GPU runtime and hardware access via the `docker-compose.jetson.yml` override file.

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.jetson.yml up -d
docker-compose exec driverless bash
cd /workspace/ros2_ws && colcon build && source install/setup.bash
```

**What's different:**
- Adds NVIDIA runtime for GPU acceleration (CUDA/TensorRT)
- Enables privileged mode for direct hardware access (lidar, CAN busses, antenna)
- Same Ubuntu, ROS 2, Python, and dependencies as development

**Shell alias (optional):**
```bash
echo "alias dc-jetson='docker-compose -f docker-compose.yml -f docker-compose.jetson.yml'" >> ~/.bashrc
```