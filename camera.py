from math import cos, radians, sin

from pyrr import Vector3, matrix44, vector, vector3


class Camera:

    def __init__(self):
        self.camera_pos = Vector3([1.0, 0.0, 25.0])
        self.camera_target = Vector3([0.0, 0.0, 0.0])

        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.camera_right = Vector3([1.0, 0.0, 0.0])

        self.mouse_sens = 0.25
        self.jaw = -90
        self.pitch = 0
        self.roll = 0

    def get_view_matrix(self):
        return matrix44.create_look_at(self.camera_pos, self.camera_pos * self.camera_front, self.camera_up)

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.mouse_sens
        y_offset *= self.mouse_sens

        self.jaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 45:
                self.pitch = 45
            elif self.pitch < -45:
                self.pitch = -45

        self.update_camera_vectors()

    def update_camera_vectors(self):
        front = Vector3([0.0, 0.0, 0.0])
        front.x = cos(radians(self.jaw)) * cos(radians(self.pitch))
        front.y = sin(radians(self.pitch))
        front.z = sin(radians(self.jaw)) * cos(radians(self.pitch))

        self.camera_front = vector.normalise(front)
        self.camera_right = vector.normalise(vector3.cross(self.camera_front, Vector3([0.0, 1.0, 0.0])))
        self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_front))
