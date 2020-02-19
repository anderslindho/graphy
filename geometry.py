import numpy as np

# Flat triangle
VERTICES = np.array([
    -0.5, -0.5, 0.0, 1.0, 0.5, 0.2,
    0.5, -0.5, 0.0, 1.0, 0.5, 0.2,
    0.0, 0.5, 0.0, 1.0, 0.5, 0.2,
], dtype=np.float32)

# Square made out of two triangles (index buffer)
_VERTICES = np.array([
    -0.5, -0.5, 0.0, 1.0, 0.5, 0.2,
    0.5, -0.5, 0.0, 0.0, 1.0, 0.2,
    -0.5, 0.5, 0.0, 0.0, 0.5, 1.0,
    0.5, 0.5, 0.0, 1.0, 1.0, 1.0,
], dtype=np.float32)
_INDICES = np.array([
    0, 1, 2,
    1, 2, 3,
], dtype=np.uint32)

# Cube made out of triangles (index buffer)
__VERTICES = np.array([
    -0.5, -0.5, 0.5, 1.0, 0.5, 0.2,
    0.5, -0.5, 0.5, 1.0, 0.5, 0.2,
    0.5, 0.5, 0.5, 1.0, 0.5, 0.2,
    -0.5, 0.5, 0.5, 1.0, 0.5, 0.2,

    -0.5, -0.5, -0.5, 1.0, 0.5, 0.2,
    0.5, -0.5, -0.5, 1.0, 0.5, 0.2,
    0.5, 0.5, -0.5, 1.0, 0.5, 0.2,
    -0.5, 0.5, -0.5, 1.0, 0.5, 0.2,
], dtype=np.float32)
__INDICES = np.array([
    0, 1, 2, 2, 3, 0,
    4, 5, 6, 6, 7, 4,
    4, 5, 1, 1, 0, 4,
    6, 7, 3, 3, 2, 6,
    5, 6, 2, 2, 1, 5,
    7, 4, 0, 0, 3, 7,
], dtype=np.uint32)