# Perception Stack Integration

## Overview

This document describes the **skeleton phase** of integrating the perception stack into jetson-ros2. This is a temporary intermediate step to validate system architecture before migrating the full perception pipeline from the uwfm_perception repository.

---

## Why Skeleton First?

**Goal:** Test end-to-end communication without forcing the entire team to rebuild Docker containers with perception dependencies.

**Approach:**
1. **Phase 1 (Current):** Create skeleton packages with dummy implementations → validate architecture
2. **Phase 2 (Future):** Add Docker dependencies → migrate full perception code

This allows us to verify the integration architecture works before committing to Docker changes that require team-wide rebuilds.

---

## Architecture

### Data Flow
```
lidar_driver ──(/perception/lidar_data)──> perception ──(/perception/local_cones)──> path_planning ──> controls
                   [PointCloud2]                           [ConeArray]
```

### Key Design Decisions

1. **Topic Namespacing:** `/perception/lidar_data` and `/perception/local_cones` for clear organization
2. **Interface Compatibility:** Perception publishes same `ConeArray` message as simulator (can swap sources)
3. **Frame Convention:** All data in `base_link` frame (consistent with simulator)
4. **No Docker Changes Yet:** Dependencies deferred to Phase 2

---

## Packages Created

### lidar_driver
**Purpose:** Interface to Ouster LiDAR sensor

**Current (Skeleton):**
- Publishes dummy PointCloud2 data at ~10Hz
- Topic: `/perception/lidar_data`
- Generates cone-like corridor pattern for testing

**Future (Phase 2):**
- Full Ouster SDK integration
- PCAP playback and live streaming
- Spatial filtering and downsampling

### perception
**Purpose:** Detect and classify cones from LiDAR data

**Current (Skeleton):**
- Subscribes to `/perception/lidar_data`
- Publishes to `/perception/local_cones`
- Naive clustering and tall/short classification

**Future (Phase 2):**
- Preprocessing (bounds filtering)
- Ground removal (RANSAC/voxel)
- DBSCAN clustering
- Shape-based cone detection

---

## Testing the Skeleton

### Build and Launch

Inside the Docker container:

```bash
# Build the new packages
cd /workspace/ros2_ws
colcon build --packages-select lidar_driver perception
source install/setup.bash

# Launch full pipeline
ros2 launch orchestrator push_test.launch.py
```

This launches: `lidar_driver` → `perception` → `path_planning` → `controls`

### Verify Communication

In another terminal (inside container):

```bash
source /workspace/ros2_ws/install/setup.bash

# Check topics exist
ros2 topic list | grep perception
# Should show: /perception/lidar_data, /perception/local_cones

# Check message rates
ros2 topic hz /perception/local_cones
# Should show ~10 Hz

# View cone detections
ros2 topic echo /perception/local_cones
```

### Expected Output

If working correctly, you'll see:
- `lidar_driver` publishing PointCloud2 messages
- `perception` processing and detecting ~10-20 cones
- `path_planning` receiving cone data and computing trajectory
- `controls` receiving trajectory and computing commands

---

## Phase 2: Full Integration

### Prerequisites
- [ ] Skeleton validated and working
- [ ] Team coordination for Docker rebuild

### Steps

**1. Update Docker Dependencies**

Add to `docker/Dockerfile`:
```dockerfile
# LiDAR and perception dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libeigen3-dev \
    libjsoncpp-dev \
    libspdlog-dev \
    libcurl4-openssl-dev \
    libtins-dev \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    ouster-sdk \
    scipy
```

Notify team to rebuild: `docker-compose build`

**2. Migrate lidar_driver Content**

From `uwfm_perception/ros2_ws/src/lidar_driver/lidar_driver/lidar_node.py`:
- Copy full Ouster driver implementation
- Update topic name from `/lidar_data` to `/perception/lidar_data`
- Verify PCAP playback works

**3. Migrate perception Content**

From `uwfm_perception/ros2_ws/src/perception_stack/perception_stack/`:
- Copy: `perception_node.py`, `preprocessor.py`, `ground_filter.py`, `shape_filter.py`
- Copy: `lidar_datatypes.py`, `perception_settings.py`
- Skip: `viz.py` (using Foxglove for visualization)
- Update topic names: `/lidar_data` → `/perception/lidar_data`, publish to `/perception/local_cones`
- Update imports (package name changed from `perception_stack` to `perception`)

**4. Test with Real Data**

- Run with PCAP recordings from actual LiDAR
- Verify cone detection accuracy
- Test interchangeably with simulator (both publish to `/perception/local_cones`)
- Validate path planning integration

---

## Troubleshooting

**Packages not found:**
```bash
source /workspace/ros2_ws/install/setup.bash
```

**Need to rebuild:**
```bash
cd /workspace/ros2_ws
colcon build --packages-select lidar_driver perception
source install/setup.bash
```

**Check nodes are running:**
```bash
ros2 node list
ros2 node info /perception
```

---

## Current Status

- [x] Skeleton packages created with standard ROS2 structure
- [x] Topic namespacing configured correctly
- [x] Interface compatibility with simulator verified
- [x] Launch file for full pipeline testing
- [x] Skeleton validated working
- [ ] Docker dependencies added
- [ ] Full content migrated
- [ ] Tested with real LiDAR data
