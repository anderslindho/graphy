from math import cos, radians, sin

from pyrr import Vector3, matrix44, vector, vector3

from config import TRACKING_CAMERA_VIEW, INVERT_MOUSE


class Camera:

    def __init__(self):
        self.camera_pos = Vector3([0.0, 0.0, 25.0])
        self.world_centre = Vector3([0.0, 0.0, 0.0])

        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.camera_right = Vector3([1.0, 0.0, 0.0])

        self.mouse_sens = 0.25
        self.velocity = 1.0
        self.distance = 25.0

        self.yaw = 90.0 if TRACKING_CAMERA_VIEW else -90.0  # FIXME: just sort out the calculations...
        self.pitch = 0.0
        self.roll = 0.0

        self.direction = {direction: False for direction in "FORWARD BACKWARD LEFT RIGHT UP DOWN".split()}

    def get_view_matrix(self):
        if TRACKING_CAMERA_VIEW:
            return matrix44.create_look_at(self.camera_pos, self.world_centre, self.camera_up)
        else:
            return matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

    def keyboard_press(self, direction):
        if TRACKING_CAMERA_VIEW:
            return

        self.direction[direction] = True

    def keyboard_release(self, direction):
        if TRACKING_CAMERA_VIEW:
            return

        self.direction[direction] = False

    def move(self):
        """WASD controls"""
        if self.direction["FORWARD"]:
            self.camera_pos += self.camera_front * self.velocity
        elif self.direction["BACKWARD"]:
            self.camera_pos -= self.camera_front * self.velocity
        if self.direction["LEFT"]:
            self.camera_pos -= self.camera_right * self.velocity
        elif self.direction["RIGHT"]:
            self.camera_pos += self.camera_right * self.velocity
        if self.direction["UP"]:
            self.camera_pos += self.camera_up * self.velocity
        elif self.direction["DOWN"]:
            self.camera_pos -= self.camera_up * self.velocity

    def mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        if INVERT_MOUSE:
            y_offset *= -1
        x_offset *= self.mouse_sens
        y_offset *= self.mouse_sens if not TRACKING_CAMERA_VIEW else -1 * self.mouse_sens

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 45:
                self.pitch = 45.0
            elif self.pitch < -45:
                self.pitch = -45.0

        if TRACKING_CAMERA_VIEW:
            self.track_update_camera_vectors()
        else:
            self.look_update_camera_vectors()

    def scroll_movement(self, steps):
        if not TRACKING_CAMERA_VIEW:  # At least temporarily
            return

        self.distance += steps

        if self.distance < 0.1:
            self.distance = 0.1
        elif self.distance > 120:
            self.distance = 120.0

        if TRACKING_CAMERA_VIEW:
            self.track_update_camera_vectors()
        else:
            self.look_update_camera_vectors()

    def look_update_camera_vectors(self):
        front = Vector3([0.0, 0.0, 0.0])
        front.x = cos(radians(self.yaw)) * cos(radians(self.pitch))
        front.y = sin(radians(self.pitch))
        front.z = sin(radians(self.yaw)) * cos(radians(self.pitch))

        self.camera_front = vector.normalise(front)
        self.camera_right = vector.normalise(vector3.cross(self.camera_front, self.camera_up))
        # self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_front))

    def track_update_camera_vectors(self):
        pos = Vector3([0.0, 0.0, 0.0])
        pos.x = self.distance * cos(radians(self.yaw)) * cos(radians(self.pitch))
        pos.y = self.distance * sin(radians(self.pitch))
        pos.z = self.distance * sin(radians(self.yaw)) * cos(radians(self.pitch))

        self.camera_pos = pos
        self.camera_right = vector.normalise(vector3.cross(self.world_centre, self.camera_up))

