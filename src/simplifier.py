from math import sin
from terrain import Face, TerrainGraph, TerrainNode


def surface_simplifier(S: TerrainGraph, theta_m: float, eps: float):
    def delta(S_tilde: TerrainGraph) -> float:
        m = float('-inf')
        for face in S.faces:
            for face_t in S_tilde.overlapping_faces(face):
                m = max(lam(face, face_t), m)
        return m

    def lam(face: Face, face_t: Face) -> float:
        return mr(face, face_t) * mr(face_t, face)

    def mr(face: Face, face_t: Face) -> float:

        theta_t_max = min(theta_m, face_t.angle())

        psuedo_path_slope = lambda x: 1 + x

        def maximize(theta) -> float:
            (sin(max(psuedo_path_slope(theta), theta_m)) /
             sin(theta_m)) * (psuedo_path_slope(theta) / theta)

        m = float('-inf')

        for i in range(0, 100 * theta_t_max):
            i = i / 100
            m = max(maximize(i), m)

        return m

    # Here we will perform a simple BFS - we want to find the node that satisfies the constraints that has the fewest vertices.
    # Keep removing vertices until we cant

    queue = [S]

    while len(queue):
        surface = queue.pop(0)

        last = len(queue) == 0
        for node in surface.rot:
            surface_tilde = surface.remove_node(node)
            surface_tilde.triangulate()
            if delta(surface_tilde) < 1.0 + eps:
                queue.append(surface_tilde)

        if last and len(queue) == 0:
            return surface
