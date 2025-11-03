import os
import yaml
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray


class ConeMapPublisher(Node):
    def __init__(self):
        super().__init__("cone_map_pub")

        self.declare_parameter("map_yaml", "")
        self.declare_parameter("world_frame", "map")   # default to map
        self.declare_parameter("cone_scale", 0.4)

        # read params
        path = self.get_parameter("map_yaml").get_parameter_value().string_value
        world_frame = self.get_parameter("world_frame").get_parameter_value().string_value
        cone_scale = float(self.get_parameter("cone_scale").value)

        if not path or not os.path.exists(path):
            raise RuntimeError(f"map_yaml not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        # if YAML says a frame, use it, otherwise fall back to world_frame param
        yaml_frame = str(data.get("frame_id", world_frame))
        cones = data.get("cones", []) or []

        pts = []
        for c in cones:
            try:
                pts.append((float(c["x"]), float(c["y"])))
            except Exception:
                pass

        self.get_logger().info(f"Loaded {len(pts)} cones from {path}")
        if not pts:
            self.get_logger().warn("No cones parsed; will publish an empty array")

        # build 1 MarkerArray with 1 POINTS marker
        marker = Marker()
        marker.header.frame_id = yaml_frame
        marker.ns = "global_cones"
        marker.id = 0
        marker.type = Marker.POINTS
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = cone_scale
        marker.scale.y = cone_scale
        marker.color.r = 0.84
        marker.color.g = 0.13
        marker.color.b = 0.13
        marker.color.a = 1.0
        marker.points = [Point(x=x, y=y, z=0.0) for (x, y) in pts]

        self.msg = MarkerArray()
        self.msg.markers = [marker]

        self.pub = self.create_publisher(MarkerArray, "/global_cones", 1)
        self.timer = self.create_timer(1.0, self._tick)

    def _tick(self):
        now = self.get_clock().now().to_msg()
        for m in self.msg.markers:
            m.header.stamp = now
        self.pub.publish(self.msg)


def main():
    rclpy.init()
    node = ConeMapPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
