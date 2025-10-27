#!/bin/bash
# Run the autonomous vehicle demo

set -e

echo "Starting autonomous vehicle demo..."
echo "=========================================="
echo "This will launch:"
echo "  - sim_world: Vehicle physics simulator with cone corridor"
echo "  - planner_local: Midline trajectory planner"
echo "  - controls_shadow: Pure pursuit controller"
echo "=========================================="
echo ""

# Get the script's directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/docker"

docker-compose run --rm driverless bash -c "
  cd /workspace/ros2_ws && \
  source /opt/ros/jazzy/setup.bash && \
  source install/setup.bash && \
  ros2 launch sim_world loop_demo.launch.py
"
