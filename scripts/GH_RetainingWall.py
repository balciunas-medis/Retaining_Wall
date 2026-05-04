# =============================================================================
# GH_RetainingWall.py
# Grasshopper Python Script — Retaining Wall in Tekla Structures
# =============================================================================
#
# Paste this code into a Grasshopper "Python Script" component (GhPython).
#
# COMPONENT INPUTS — add the following in the component's input list:
#   run    (bool)  — Set True to create/update model elements
#   x      (float) — X coordinate of base slab origin [mm]
#   y      (float) — Y coordinate of base slab origin [mm]
#   z      (float) — Z coordinate of base slab bottom [mm]
#   L      (float) — Wall length along the Y axis [mm]
#   H      (float) — Stem height above top of base slab [mm]
#   B      (float) — Total base width [mm]
#   t_stem (float) — Stem wall thickness [mm]
#   t_base (float) — Base slab thickness [mm]
#   toe    (float) — Toe length (from base left edge to stem front face) [mm]
#   mat    (str)   — Tekla material name, e.g. "C30" or "C25/30"
#   pfx    (str)   — Part number prefix, e.g. "RW"
#
# COMPONENT OUTPUTS:
#   out    — Script output log (auto-provided by GhPython)
#   msg    — Human-readable status / result message
#
# REQUIREMENTS:
#   - Rhinoceros 7+ with Grasshopper
#   - Tekla Structures 2020 or later (must be open with a model)
#   - Tekla Open API DLLs accessible on the machine
#     (typically in C:\Program Files\Tekla Structures\<version>\bin\)
#
# WALL GEOMETRY (cross-section, looking along +Y):
#
#         +-------+
#         | STEM  |  height H, thickness t_stem
#         |       |
#   ------+-------+--------
#   |       BASE SLAB      |  thickness t_base, width B
#   +----------------------+
#    <toe><t_stem><- heel ->
#    <-------- B --------->
#
# =============================================================================

import clr

# ---------------------------------------------------------------------------
# Load Tekla Open API assemblies.
# If the DLLs are not on the system PATH you can load them explicitly, e.g.:
#   clr.AddReferenceToFileAndPath(
#       r"C:\Program Files\Tekla Structures\2023\bin\Tekla.Structures.Model.dll"
#   )
# ---------------------------------------------------------------------------
clr.AddReference("Tekla.Structures.Model")
clr.AddReference("Tekla.Structures.Geometry3d")

from Tekla.Structures.Model import (
    Model,
    ContourPlate,
    Contour,
    ContourPoint,
    Position,
)
from Tekla.Structures.Geometry3d import Point


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_contour_plate(profile_str, material, prefix, name, cls,
                         points, depth_enum):
    """Create and insert a ContourPlate; return the plate or None on failure."""
    plate = ContourPlate()
    plate.Profile.ProfileString = profile_str
    plate.Material.MaterialString = material
    plate.PartNumber.Prefix = prefix
    plate.Name = name
    plate.Class = cls
    plate.Position.Depth = depth_enum

    contour = Contour()
    for pt in points:
        contour.AddContourPoint(ContourPoint(pt, None))
    plate.Contour = contour

    return plate if plate.Insert() else None


# ---------------------------------------------------------------------------
# Main wall creation function
# ---------------------------------------------------------------------------

def create_retaining_wall(model, x, y, z, L, H, B, t_stem, t_base, toe,
                           mat, pfx):
    """
    Create retaining wall elements (base slab + stem) in Tekla Structures.

    All dimensions in millimetres.
    Returns a list of status strings, one per element.
    """
    log = []

    # ------------------------------------------------------------------
    # 1. Base slab — horizontal ContourPlate
    #    Contour at z (bottom face); plate grows upward (ABOVE).
    # ------------------------------------------------------------------
    base_pts = [
        Point(x,         y,         z),
        Point(x + B,     y,         z),
        Point(x + B,     y + L,     z),
        Point(x,         y + L,     z),
    ]
    base = _make_contour_plate(
        profile_str="PL{}".format(int(t_base)),
        material=mat,
        prefix=pfx,
        name="BASE_SLAB",
        cls="1",
        points=base_pts,
        depth_enum=Position.DepthEnum.ABOVE,
    )
    log.append("Base slab : {}".format("OK" if base else "FAILED"))

    # ------------------------------------------------------------------
    # 2. Stem wall — vertical ContourPlate
    #    Contour on the front face of the stem (x = x + toe);
    #    plate grows toward the heel side (BEHIND).
    # ------------------------------------------------------------------
    stem_x     = x + toe
    stem_z_bot = z + t_base
    stem_z_top = z + t_base + H

    stem_pts = [
        Point(stem_x,     y,         stem_z_bot),
        Point(stem_x,     y + L,     stem_z_bot),
        Point(stem_x,     y + L,     stem_z_top),
        Point(stem_x,     y,         stem_z_top),
    ]
    stem = _make_contour_plate(
        profile_str="PL{}".format(int(t_stem)),
        material=mat,
        prefix=pfx,
        name="STEM",
        cls="2",
        points=stem_pts,
        depth_enum=Position.DepthEnum.BEHIND,
    )
    log.append("Stem      : {}".format("OK" if stem else "FAILED"))

    # Commit all inserted objects to the model at once
    model.CommitChanges()

    return log


# ---------------------------------------------------------------------------
# Entry point — executed by Grasshopper each time inputs change
# ---------------------------------------------------------------------------

msg = "Set 'run' to True to create wall elements."

if run:  # 'run' is a GH input variable
    try:
        model = Model()
        if model.GetConnectionStatus():
            results = create_retaining_wall(
                model,
                float(x), float(y), float(z),
                float(L), float(H), float(B),
                float(t_stem), float(t_base), float(toe),
                str(mat), str(pfx),
            )
            msg = "\n".join(results)
        else:
            msg = "ERROR: Not connected to Tekla Structures. " \
                  "Open a model in Tekla first."
    except Exception as e:
        msg = "ERROR: {}".format(e)
