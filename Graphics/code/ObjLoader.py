# I'm writing this file because I'm too stupid for my own good
# Pray for me


class ObjData:
    size = 0
    positions = []
    normals = []
    uvs = []
    materialIndexes = []
    materials = {}

    def __init__(self, size, positions, normals, uvs, materialIndexes, materials):
        self.size = size
        self.positions = positions
        self.normals = normals
        self.uvs = uvs
        self.materialIndexes = materialIndexes
        self.materials = materials


def load_obj(filename):
    (positions, normals, uvs, materials, materialIndexes) = parse_lines(filename)
    return process_material_chunks(positions, normals, uvs, materials, materialIndexes)


def parse_lines(filename):
    """Parse the lines of an .obj file
    This performs no processing - just raw data reading
    """
    positions = []
    normals = []
    uvs = []

    materials = {}
    materialIndexes = []

    # Open the file and handle the internal lines
    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) > 0 and line[:1] != "#":
                tokens = line.split()
                action = tokens[0]
                if action == "mtllib":
                    # Named definition for an external MTL file
                    pass
                elif action == "usemtl":
                    # Material to use -> from the MTL file (above)
                    materialName = " ".join(tokens[1:])
                    if (
                        len(materialIndexes) == 0
                        or materialIndexes[-1][0] != materialName
                    ):
                        materialIndexes.append([materialName, []])
                elif action == "v":
                    # Geometric vertex
                    # (x, y, z [,w]) coordinates
                    positions.append([float(v) for v in tokens[1:4]])
                elif action == "vn":
                    # Vertex normals
                    # (x, y, z) -> not guaranteed to be unit vectors
                    normals.append([float(v) for v in tokens[1:4]])
                elif action == "vt":
                    # Texture UVs
                    # (u, [,v, w]) coordinates
                    uvs.append([float(v) for v in tokens[1:4]])
                elif action == "vp":
                    # Parameter space vertices
                    # Not relevant
                    pass
                elif action == "f":
                    # Polygonal faces
                    materialIndexes[-1][1] += parse_face(tokens[1:])
                elif action == "o":
                    # Object groupings
                    # Not relevant
                    pass
                elif action == "s":
                    # Smoothing groups
                    # Also not relevant
                    pass

    return positions, normals, uvs, materials, materialIndexes


def parse_face(face):
    """Parse a single face of an .obj file
    Faces are given as a list of triangles
    Each triangle is a list of vertices seperated by /

    Arguments:
        face {list} -- [description]

    Returns:
        list -- [description]
    """

    result = []
    v0 = parse_face_indexes(face[0])
    v1 = parse_face_indexes(face[1])
    for f in face[2:]:
        v2 = parse_face_indexes(f)
        result += [v0, v1, v2]
        v1 = v2

    return result


def parse_face_indexes(s):
    """Split a triangle face into the relevant indices

    Arguments:
        s {str} -- [description]

    Returns:
        list -- [description]
    """
    return [int(ind) - 1 if ind != "" else -1 for ind in s.split("/")]


def process_material_chunks(positions, normals, uvs, materials, materialIndexes):
    # Count the number of vertices in this file
    size = 0
    for mat in materialIndexes:
        size += len(mat[1])

    processed_positions = [None] * size
    processed_normals = [None] * size
    processed_uvs = [[0, 0]] * size
    processed_materials = []

    # Deindex the mesh
    start = 0
    end = 0
    for id, triangles in materialIndexes:
        # TODO: Process the actual materials

        # Calculate the offset and size of this material
        start = end
        end = start + int(len(triangles) / 3)
        offset = start * 3
        length = len(triangles)

        # Deindexing
        for i in range(0, len(triangles), 3):
            for j in range(3):
                triangle = triangles[i + j]
                voffset = offset + i + j
                processed_positions[voffset] = positions[triangle[0]]
                processed_normals[voffset] = normals[triangle[2]]
                if triangle[1] != -1:
                    processed_uvs[voffset] = uvs[triangle[1]]

        processed_materials.append((id, offset, length))

    return ObjData(
        size,
        processed_positions,
        processed_normals,
        processed_uvs,
        processed_materials,
        {},
    )
