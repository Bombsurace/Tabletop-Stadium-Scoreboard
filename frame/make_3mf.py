"""Bundle a front and its yard-line inlay into one 3MF: a single object with two parts.
Bambu Studio / OrcaSlicer / PrusaSlicer open it as one object; assign white to the 'lines' part."""
import os, sys, zipfile
import trimesh


def mesh_xml(oid, name, m):
    v = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.vertices)
    t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return f'<object id="{oid}" type="model" name="{name}"><mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>'


def write_3mf(path, parts, name):
    """parts: list of (part_name, stl_path)"""
    objs, comps = [], []
    for i, (pname, stl) in enumerate(parts, start=1):
        m = trimesh.load(stl)
        objs.append(mesh_xml(i, pname, m))
        comps.append(f'<component objectid="{i}"/>')
    top = len(parts) + 1
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<metadata name="Title">{name}</metadata><resources>' + "".join(objs) +
             f'<object id="{top}" type="model" name="{name}"><components>{"".join(comps)}</components></object>'
             f'</resources><build><item objectid="{top}"/></build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "stl"
    for key in ("standard7", "wide79"):
        f, l = os.path.join(d, f"front_{key}.stl"), os.path.join(d, f"front_{key}_lines.stl")
        if os.path.exists(f) and os.path.exists(l):
            out = os.path.join(d, f"front_{key}_2color.3mf")
            write_3mf(out, [("field", f), ("lines (white)", l)], f"front_{key}")
            print("wrote", out)
