#!/usr/bin/env python3
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from interfaces.msg import ConeArray, Trajectory, TrajectoryPoint

class PlannerLocal(Node):
    """
    Very naive 'midline' planner:
    - Subscribes /perception/local_cones (base_link frame)
    - Publishes /planning/trajectory (Trajectory in base_link frame)
    """
    def __init__(self):
        super().__init__('path_planning')
        self.traj_pub = self.create_publisher(Trajectory, '/planning/trajectory', 10)
        self.sub = self.create_subscription(ConeArray, '/perception/local_cones', self.on_cones, 10)

    def on_cones(self, msg: ConeArray):
        if not msg.cones:
            self.traj_pub.publish(Trajectory(header=msg.header, points=[]))
            return

        pts = np.array([[c.x, c.y] for c in msg.cones], dtype=np.float32)
        xs = np.linspace(1.0, 15.0, 15)
        path_xy = []
        for x in xs:
            near = pts[np.abs(pts[:, 0] - x) < 1.0]
            y_mid = 0.0 if near.size == 0 else float(np.mean(near[:, 1]))
            path_xy.append((float(x), y_mid))

        traj = Trajectory()
        traj.header = Header()
        traj.header.stamp = msg.header.stamp
        traj.header.frame_id = 'base_link'  # push-test convenience

        traj.points = []
        for x, y in path_xy:
            tp = TrajectoryPoint()
            tp.pose.position.x = x
            tp.pose.position.y = y
            tp.pose.orientation.w = 1.0  # yaw ~ 0 in base_link
            tp.v_des = 1.0
            tp.a_des = 0.0
            traj.points.append(tp)

        self.traj_pub.publish(traj)
        self.get_logger().info(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        self.get_logger().info(f'📍 PATH PLANNER:')
        self.get_logger().info(f'   Received: {len(msg.cones)} cones')
        self.get_logger().info(f'   Computed: {len(traj.points)} waypoints')
        self.get_logger().info(f'   Target speed: 1.0 m/s')
        self.get_logger().info(f'📡 Publishing trajectory to /planning/trajectory')

def main():
    rclpy.init()
    rclpy.spin(PlannerLocal())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
