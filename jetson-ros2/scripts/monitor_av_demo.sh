#!/bin/bash
# Monitor the autonomous vehicle demo topics

set -e

echo "Autonomous Vehicle Demo - Topic Monitor"
echo "========================================"
echo ""

# Get the script's directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/docker"

docker-compose run --rm driverless bash -c "
  cd /workspace/ros2_ws && \
  source /opt/ros/jazzy/setup.bash && \
  source install/setup.bash && \
  echo 'Available topics:' && \
  echo '' && \
  ros2 topic list && \
  echo '' && \
  echo 'Key topics:' && \
  echo '  /perception/local_cones - Detected cone positions' && \
  echo '  /planning/trajectory - Planned path' && \
  echo '  /controls/command - Steering/throttle commands' && \
  echo '  /state/odom - Vehicle position and velocity' && \
  echo '' && \
  echo 'To view a topic, run:' && \
  echo '  ros2 topic echo /topic/name' && \
  echo '' && \
  bash
"
