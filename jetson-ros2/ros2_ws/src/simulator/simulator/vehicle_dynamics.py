import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist

def clamp(x, lo, hi): return max(lo, min(hi, x))
def sgn(x): return 0.0 if abs(x) < 1e-6 else (1.0 if x > 0 else -1.0)

class TorqueVehicle(Node):
    """
    Bare-bones torque-driven vehicle:
      - Inputs on /control_action (Twist):
          * torque_cmd = msg.linear.x  [N·m]  (applied to all 4 wheels)
          * steer_phi  = msg.angular.z [rad]  (front-wheel steer angle)
      - Publishes /vehicle_pose (PoseStamped, frame='map')

    """

    def __init__(self):
        super().__init__('torque_vehicle')

        # ---------- Tunable parameters (defaults ~light RWD sports car) ----------
        g = 9.81
        self.declare_parameter('dt', 0.01)                 # 100 Hz
        self.declare_parameter('L', 2.31)                  # wheelbase [m] (MX-5 ND)
        self.declare_parameter('mass', 1100.0)             # vehicle mass [kg]
        self.declare_parameter('wheel_radius', 0.308)      # rolling radius [m] (≈ 205/45R17)
        self.declare_parameter('Jw', 0.80)                 # wheel inertia per wheel [kg·m^2]
        self.declare_parameter('mu_long', 0.80)            # dry asphalt peak μ (longitudinal)
        self.declare_parameter('slip_slope', 10.0)         # tanh gain k_s for F-x(κ)
        self.declare_parameter('Crr', 0.013)               # rolling resistance coeff
        self.declare_parameter('rho_air', 1.225)           # air density [kg/m^3]
        self.declare_parameter('Cd', 0.35)                 # drag coefficient
        self.declare_parameter('frontal_area', 1.82)       # frontal area [m^2]
        self.declare_parameter('wheel_drag_c', 0.02)       # viscous wheel loss [N·m/(rad/s)]
        self.declare_parameter('cmd_timeout', 0.25)        # [s] timeout → zero torque / straight
        self.declare_parameter('yaw_rate_limit', 3.0)      # [rad/s] safety clamp

        # Cache params
        self.dt     = float(self.get_parameter('dt').value)
        self.L      = float(self.get_parameter('L').value)
        self.m      = float(self.get_parameter('mass').value)
        self.R      = float(self.get_parameter('wheel_radius').value)
        self.Jw     = float(self.get_parameter('Jw').value)
        self.mu     = float(self.get_parameter('mu_long').value)
        self.k_s    = float(self.get_parameter('slip_slope').value)
        self.Crr    = float(self.get_parameter('Crr').value)
        self.rho    = float(self.get_parameter('rho_air').value)
        self.Cd     = float(self.get_parameter('Cd').value)
        self.A      = float(self.get_parameter('frontal_area').value)
        self.c_omega= float(self.get_parameter('wheel_drag_c').value)
        self.timeout= float(self.get_parameter('cmd_timeout').value)
        self.rdot_lim = float(self.get_parameter('yaw_rate_limit').value)

        # ---------- State ----------
        # Pose & body speed
        self.x = 0.0; self.y = 0.0; self.psi = 0.0
        self.u = 0.0    # longitudinal speed at CG [m/s] (no lateral v in this minimal model)

        # Wheels: FL, FR, RL, RR (but symmetric here)
        self.w_omega = [0.0, 0.0, 0.0, 0.0]

        # Command
        self.torque_cmd = 0.0     # N·m applied to all four wheels
        self.steer_phi  = 0.0     # rad
        self.last_cmd_time = self.get_clock().now()

        # ---------- ROS I/O ----------
        self.pose_pub = self.create_publisher(PoseStamped, '/vehicle_pose', 10)
        self.create_subscription(Twist, '/control_action', self._cmd_cb, 10)
        self.timer = self.create_timer(self.dt, self._step)
        self.get_logger().info('torque_vehicle: running (torque-per-wheel + aero/rolling)')

        # Precompute static wheel load
        self.Fz_per_wheel = self.m * g / 4.0

    def _cmd_cb(self, msg: Twist):
        # linear.x = torque per wheel [N·m] (single value applied to all wheels)
        # angular.z = steering angle Φ [rad]
        self.torque_cmd = float(msg.linear.x)
        self.steer_phi  = float(msg.angular.z)
        self.last_cmd_time = self.get_clock().now()

    def _tire_longitudinal_force(self, kappa, Fz):
        # Smooth saturation: F_x = μ Fz * tanh(k_s * κ)
        return self.mu * Fz * math.tanh(self.k_s * kappa)

    def _step(self):
        now = self.get_clock().now()
        age = (now - self.last_cmd_time).nanoseconds * 1e-9

        # If command stale: zero torque, center steering
        torque = 0.0 if age > self.timeout else self.torque_cmd
        phi    = 0.0 if age > self.timeout else self.steer_phi

        # --- Per-wheel rotational dynamics + tire forces ---
        Fx_wheels = [0.0, 0.0, 0.0, 0.0]
        for i in range(4):
            # Slip ratio (use CG u as wheel ground speed for simplicity)
            u_ground = self.u
            denom = max(abs(u_ground), 0.1)  # epsilon to avoid div by 0, limits huge κ at standstill
            kappa = (self.R * self.w_omega[i] - u_ground) / denom

            # Tire longitudinal force with smooth saturation
            Fx = self._tire_longitudinal_force(kappa, self.Fz_per_wheel)
            Fx_wheels[i] = Fx

            # Wheel ODE
            Twheel = torque
            # Resistive torque from contact patch + a small viscous wheel loss
            T_resist = self.R * Fx + self.c_omega * self.w_omega[i]
            domega = (Twheel - T_resist) / max(self.Jw, 1e-6)
            self.w_omega[i] += domega * self.dt
            # keep ω physically reasonable
            self.w_omega[i] = clamp(self.w_omega[i], -1000.0, 1000.0)

        # --- Chassis longitudinal dynamics ---
        Fx_total = sum(Fx_wheels)  # traction (can be negative if braking torque used)
        F_drag = 0.5 * self.rho * self.Cd * self.A * (self.u ** 2)
        F_rr   = self.Crr * self.m * 9.81 * sgn(self.u)
        # If almost stopped, kill tiny forces to avoid jitter
        if abs(self.u) < 0.05 and abs(torque) < 1e-2:
            F_rr = 0.0

        u_dot = (Fx_total - F_drag - F_rr) / self.m
        self.u += u_dot * self.dt
        # numerical clean-up
        if abs(self.u) < 1e-3 and abs(torque) < 1e-2:
            self.u = 0.0

        # --- Simple lateral/yaw via kinematic bicycle (using speed u) ---
        psi_dot = 0.0 if abs(self.L) < 1e-6 else (self.u / self.L) * math.tan(phi)
        psi_dot = clamp(psi_dot, -self.rdot_lim, self.rdot_lim)
        self.psi += psi_dot * self.dt
        self.psi = math.atan2(math.sin(self.psi), math.cos(self.psi))

        # --- Integrate position in map frame ---
        self.x += self.u * math.cos(self.psi) * self.dt
        self.y += self.u * math.sin(self.psi) * self.dt

        # --- Publish pose ---
        out = PoseStamped()
        out.header.stamp = now.to_msg()
        out.header.frame_id = 'map'
        out.pose.position.x = self.x
        out.pose.position.y = self.y
        out.pose.position.z = 0.0
        out.pose.orientation.x = 0.0
        out.pose.orientation.y = 0.0
        out.pose.orientation.z = math.sin(self.psi * 0.5)
        out.pose.orientation.w = math.cos(self.psi * 0.5)
        self.pose_pub.publish(out)

def main():
    rclpy.init()
    node = TorqueVehicle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
