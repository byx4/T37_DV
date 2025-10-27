#!/bin/bash
# Build the autonomous vehicle demo packages

set -e

echo "Building autonomous vehicle demo packages..."
echo "=========================================="

# Get the script's directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/docker"

# Build Docker image with dependencies
echo "Step 1: Building Docker image..."
docker-compose build

# Build ROS workspace inside container
echo "Step 2: Building ROS workspace..."
docker-compose run --rm driverless bash -c "
  cd /workspace/ros2_ws && \
  source /opt/ros/jazzy/setup.bash && \
  colcon build --packages-select contracts sim_world planner_local controls_shadow --symlink-install
"

echo "=========================================="
echo "Build complete! Run ./scripts/run_av_demo.sh to start the autonomous vehicle demo."
