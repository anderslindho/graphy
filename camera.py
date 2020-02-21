from math import cos, radians, sin

from pyrr import Vector3, matrix44, vector, vector3, quaternion

TRACKING_CAMERA_VIEW = True


class Camera:

    def __init__(self):
        self.camera_pos = Vector3([0.0, 0.0, 25.0])
        self.world_centre = Vector3([0.0, 0.0, 0.0])

        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.camera_right = Vector3([1.0, 0.0, 0.0])

        self.look_around_mouse_sens = 0.25
        self.track_mouse_sens = 0.01
        self.distance = 25.0
        self.jaw = -90.0
        self.pitch = 0.0
        self.roll = 0.0

    def get_view_matrix(self):
        if TRACKING_CAMERA_VIEW:
            return matrix44.create_look_at(self.camera_pos, self.world_centre, self.camera_up)
        else:
            return matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

    def look_around_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.look_around_mouse_sens
        y_offset *= self.look_around_mouse_sens

        self.jaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 45:
                self.pitch = 45.0
            elif self.pitch < -45:
                self.pitch = -45.0

        self.look_around_update_camera_vectors()

    def look_around_update_camera_vectors(self):
        front = Vector3([0.0, 0.0, 0.0])
        front.x = cos(radians(self.jaw)) * cos(radians(self.pitch))
        front.y = sin(radians(self.pitch))
        front.z = sin(radians(self.jaw)) * cos(radians(self.pitch))

        self.camera_front = vector.normalise(front)
        self.camera_right = vector.normalise(vector3.cross(self.camera_front, Vector3([0.0, 1.0, 0.0])))
        self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_front))

    def track_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.track_mouse_sens
        y_offset *= self.track_mouse_sens

        self.jaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 45:
                self.pitch = 45.0
            elif self.pitch < -45:
                self.pitch = 45.0

        self.track_update_camera_vectors()

    def track_update_camera_vectors(self):
        pos = Vector3([0.0, 0.0, 0.0])
        pos.x = self.distance * cos(self.jaw)
        pos.y = 0
        pos.z = self.distance * sin(self.jaw)

        self.camera_pos = pos
        self.camera_right = vector.normalise(vector3.cross(self.camera_front, self.camera_up))

