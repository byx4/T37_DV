#!/usr/bin/env python3
"""
Orchestrator Node - Central coordination for the driverless system.

The orchestrator is responsible for:
- System-level setup and configuration
- Tracking the current autonomous mission
- Top-level control flow management

Currently this node is a placeholder that maintains mission state internally
without interaction with other system components. Future development will add:
- CAN message integration for mission selection and control
- Dynamic node lifecycle management
- System health monitoring and fault handling
"""

import rclpy
from rclpy.node import Node
from enum import Enum, auto


class AutonomousMission(Enum):
    """Autonomous mission types for Formula Student Driverless competitions."""
    MANUAL = auto()          # Manual driving mode
    INSPECTION = auto()      # Pre-competition inspection
    ACCELERATION = auto()    # Acceleration event
    SKIDPAD = auto()        # Skidpad event
    AUTOCROSS = auto()      # Autocross event
    TRACKDRIVE = auto()     # Trackdrive event
    EBS_TEST = auto()       # Emergency brake system test


class OrchestratorNode(Node):
    """
    Central orchestration node for the driverless system.
    
    This node serves as the top-level controller, managing system state
    and coordinating between subsystems. Currently in development.
    """

    def __init__(self):
        super().__init__('orchestrator_node')
        
        # Initialize mission state
        self._current_mission = AutonomousMission.MANUAL
        
        self.get_logger().info('Orchestrator node initialized')
        self.get_logger().info(f'Current mission: {self._current_mission.name}')
        
        # Timer for periodic logging (development placeholder)
        self.create_timer(5.0, self.timer_callback)

    def timer_callback(self):
        """Periodic callback for development monitoring."""
        self.get_logger().info(
            f'Orchestrator active - Mission: {self._current_mission.name}',
            throttle_duration_sec=10.0
        )

    def set_mission(self, mission: AutonomousMission):
        """
        Set the current autonomous mission.
        
        Args:
            mission: The autonomous mission to set
        """
        self._current_mission = mission
        self.get_logger().info(f'Mission changed to: {mission.name}')

    def get_mission(self) -> AutonomousMission:
        """
        Get the current autonomous mission.
        
        Returns:
            The current autonomous mission
        """
        return self._current_mission


def main(args=None):
    """Main entry point for the orchestrator node."""
    rclpy.init(args=args)
    
    orchestrator = OrchestratorNode()
    
    try:
        rclpy.spin(orchestrator)
    except KeyboardInterrupt:
        pass
    finally:
        orchestrator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

