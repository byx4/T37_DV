#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

from std_msgs.msg import Header
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped

from interfaces.msg import Cone, ConeArray, Control

import tf2_ros

DT = 0.02  # internal sim step @ 50 Hz

def yaw_to_quat(z_yaw_rad: float):
    """Return quaternion (x,y,z,w) for a yaw-only rotation."""
    half = 0.5 * z_yaw_rad
    return (0.0, 0.0, math.sin(half), math.cos(half))

class SimWorld(Node):
    """
    Tiny bicycle-model simulator.
    - Subscribes to /controls/command (contracts/Control)
    - Publishes /state/odom (nav_msgs/Odometry) and TF (odom->base_link)
    - Publishes /perception/local_cones (contracts/ConeArray) in base_link frame
    """
    def __init__(self):
        super().__init__('simulator')

        # Parameters
        self.declare_parameter('wheelbase', 1.6)
        self.declare_parameter('lane_half_width', 1.5)
        self.declare_parameter('cone_spacing', 3.0)
        self.declare_parameter('cones_ahead', 25.0)
        self.declare_parameter('publish_rate_hz', 2.0)  # Slowed down for demo visibility
        self.declare_parameter('frame_odom', 'odom')
        self.declare_parameter('frame_base', 'base_link')

        # Pub/Sub
        self.odom_pub = self.create_publisher(Odometry, '/state/odom', 10)
        self.cones_pub = self.create_publisher(ConeArray, '/perception/local_cones', 10)
        self.cmd_sub = self.create_subscription(Control, '/controls/command', self.on_cmd, 10)

        # TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Vehicle state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.v = 0.0
        self.steering = 0.0

        # Timers
        self.timer_sim = self.create_timer(DT, self.step_sim)
        self.timer_pub = self.create_timer(
            1.0 / float(self.get_parameter('publish_rate_hz').value), self.publish_cones
        )

        # Debug logging timer (every 1 second for demo)
        self.timer_log = self.create_timer(1.0, self.log_status)

    def on_cmd(self, msg: Control):
        # Simplified: Convert torque vectoring to speed (average wheel torque)
        # For demo purposes, use average torque as speed proxy
        avg_torque = (msg.t_fl + msg.t_fr + msg.t_rr + msg.t_rl) / 4.0
        self.v = avg_torque  # Simplified mapping
        self.steering = float(msg.phi)

    def step_sim(self):
        """Integrate a simple bicycle model and publish TF + odom."""
        L = float(self.get_parameter('wheelbase').value)
        beta = math.atan(0.5 * math.tan(self.steering + 1e-9))
        self.x += self.v * math.cos(self.yaw + beta) * DT
        self.y += self.v * math.sin(self.yaw + beta) * DT
        self.yaw += (self.v / L) * math.sin(beta) * 2.0 * DT

        # TF (odom -> base_link)
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.get_parameter('frame_odom').value
        t.child_frame_id = self.get_parameter('frame_base').value
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        qx, qy, qz, qw = yaw_to_quat(self.yaw)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

        # Odometry
        od = Odometry()
        od.header = t.header
        od.child_frame_id = t.child_frame_id
        od.pose.pose.position.x = self.x
        od.pose.pose.position.y = self.y
        od.pose.pose.orientation.x = qx
        od.pose.pose.orientation.y = qy
        od.pose.pose.orientation.z = qz
        od.pose.pose.orientation.w = qw
        od.twist.twist.linear.x = self.v
        self.odom_pub.publish(od)

    def publish_cones(self):
        """Publish a simple corridor of cones in base_link frame."""
        hdr = Header()
        hdr.stamp = self.get_clock().now().to_msg()
        hdr.frame_id = self.get_parameter('frame_base').value

        lane = float(self.get_parameter('lane_half_width').value)
        spacing = float(self.get_parameter('cone_spacing').value)
        max_ahead = float(self.get_parameter('cones_ahead').value)

        msg = ConeArray()
        msg.header = hdr
        s = 2.0
        cones = []
        while s < max_ahead:
            left = Cone();  left.x = s; left.y =  lane; left.is_tall = False
            right = Cone(); right.x = s; right.y = -lane; right.is_tall = False
            cones.extend([left, right])
            s += spacing
        msg.cones = cones
        self.cones_pub.publish(msg)

    def log_status(self):
        """Log current vehicle status for demo purposes."""
        self.get_logger().info(
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        )
        self.get_logger().info(
            f'🚗 VEHICLE STATE:'
        )
        self.get_logger().info(
            f'   Position: x={self.x:6.2f}m, y={self.y:6.2f}m'
        )
        self.get_logger().info(
            f'   Speed: {self.v:4.2f}m/s | Heading: {math.degrees(self.yaw):5.1f}°'
        )
        self.get_logger().info(
            f'   Steering: {math.degrees(self.steering):5.1f}°'
        )
        self.get_logger().info(
            f'📡 Publishing: Odometry @ 50Hz, Cones @ 2Hz'
        )

def main():
    rclpy.init()
    node = SimWorld()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
