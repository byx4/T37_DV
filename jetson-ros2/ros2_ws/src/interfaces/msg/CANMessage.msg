# CAN bus message
# Standard format for CAN messages on the vehicle
std_msgs/Header header
uint16 can_id           # 12-bit CAN ID (0x000 to 0xFFF for standard CAN)
uint8[8] data           # 8 bytes of CAN data

