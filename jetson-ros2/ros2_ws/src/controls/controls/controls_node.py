#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from interfaces.msg import Trajectory, Control

class ControlsShadow(Node):
    """
    Minimal controller:
    - Subscribes /planning/trajectory (base_link frame)
    - Publishes /controls/command (contracts/Control)
    Uses a simple pure-pursuit curvature approximation.
    """
    def __init__(self):
        super().__init__('controls')
        self.declare_parameter('lookahead', 3.0)
        self.declare_parameter('wheelbase', 1.6)
        self.cmd_pub = self.create_publisher(Control, '/controls/command', 10)
        self.sub = self.create_subscription(Trajectory, '/planning/trajectory', self.on_traj, 10)

    def on_traj(self, traj: Trajectory):
        if not traj.points:
            return

        Ld = float(self.get_parameter('lookahead').value)
        L = float(self.get_parameter('wheelbase').value)

        # choose first point with x >= lookahead in base_link
        target = None
        for p in traj.points:
            if p.pose.position.x >= Ld:
                target = p
                break
        if target is None:
            target = traj.points[-1]

        tx = float(target.pose.position.x)
        ty = float(target.pose.position.y)

        # Pure pursuit curvature approximation in base_link
        # If x≈Ld, kappa ≈ 2*y / Ld^2
        kappa = 2.0 * ty / max(Ld * Ld, 1e-3)
        steer = math.atan(L * kappa)
        speed = float(target.v_des)

        # Create Control message (simplified torque vectoring)
        # For demo: distribute speed equally to all wheels as torque
        out = Control()
        out.t_fl = float(speed)
        out.t_fr = float(speed)
        out.t_rr = float(speed)
        out.t_rl = float(speed)
        out.phi = float(steer)
        out.timestamp = float(self.get_clock().now().seconds_nanoseconds()[0])
        self.cmd_pub.publish(out)
        self.get_logger().info(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        self.get_logger().info(f'🎮 CONTROLLER:')
        self.get_logger().info(f'   Target point: x={tx:.2f}m, y={ty:.2f}m')
        self.get_logger().info(f'   Computed steering: {math.degrees(steer):5.1f}°')
        self.get_logger().info(f'   Commanded speed: {speed:.2f}m/s')
        self.get_logger().info(f'📡 Publishing commands to /controls/command')

def main():
    rclpy.init()
    rclpy.spin(ControlsShadow())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
