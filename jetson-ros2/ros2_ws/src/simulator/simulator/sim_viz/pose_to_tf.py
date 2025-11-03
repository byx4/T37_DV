import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TransformStamped
from tf2_ros import TransformBroadcaster

class PoseToTF(Node):
    def __init__(self):
        super().__init__('pose_to_tf')
        self.declare_parameter('pose_topic', '/vehicle_pose')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frame', 'base_link')

        self.pose_topic = self.get_parameter('pose_topic').value
        self.map_frame = self.get_parameter('map_frame').value
        self.base_frame = self.get_parameter('base_frame').value

        self.br = TransformBroadcaster(self)
        self.create_subscription(PoseStamped, self.pose_topic, self.cb, 10)

    def cb(self, msg: PoseStamped):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        # force parent frame, don’t trust incoming
        t.header.frame_id = self.map_frame
        t.child_frame_id = self.base_frame

        t.transform.translation.x = msg.pose.position.x
        t.transform.translation.y = msg.pose.position.y
        t.transform.translation.z = msg.pose.position.z
        t.transform.rotation = msg.pose.orientation

        self.br.sendTransform(t)

def main():
    rclpy.init()
    rclpy.spin(PoseToTF())
    rclpy.shutdown()
