// =============================================================================
// GH_RetainingWall.cs
// Grasshopper C# Script — Retaining Wall in Tekla Structures
// =============================================================================
//
// Paste this code into a Grasshopper "C# Script" component.
//
// COMPONENT INPUTS — add the following in the component's input list:
//   run    (bool)   — Set True to create/update model elements
//   x      (double) — X coordinate of base slab origin [mm]
//   y      (double) — Y coordinate of base slab origin [mm]
//   z      (double) — Z coordinate of base slab bottom [mm]
//   L      (double) — Wall length along the Y axis [mm]
//   H      (double) — Stem height above top of base slab [mm]
//   B      (double) — Total base width [mm]
//   t_stem (double) — Stem wall thickness [mm]
//   t_base (double) — Base slab thickness [mm]
//   toe    (double) — Toe length (from base left edge to stem front face) [mm]
//   mat    (string) — Tekla material name, e.g. "C30" or "C25/30"
//   pfx    (string) — Part number prefix, e.g. "RW"
//
// COMPONENT OUTPUTS:
//   A      — Human-readable status / result message
//
// REQUIRED REFERENCES (add in the component's "References" section):
//   Tekla.Structures.Model.dll
//   Tekla.Structures.Geometry3d.dll
//   (typically in C:\Program Files\Tekla Structures\<version>\bin\)
//
// WALL GEOMETRY (cross-section, looking along +Y):
//
//         +-------+
//         | STEM  |  height H, thickness t_stem
//         |       |
//   ------+-------+--------
//   |       BASE SLAB      |  thickness t_base, width B
//   +----------------------+
//    <toe><t_stem><- heel ->
//    <-------- B --------->
//
// =============================================================================

using System;
using System.Text;
using Tekla.Structures.Geometry3d;
using Tekla.Structures.Model;

private void RunScript(
    bool   run,
    double x,
    double y,
    double z,
    double L,
    double H,
    double B,
    double t_stem,
    double t_base,
    double toe,
    string mat,
    string pfx,
    ref object A)
{
    if (!run)
    {
        A = "Set 'run' to True to create wall elements.";
        return;
    }

    var model = new Model();
    if (!model.GetConnectionStatus())
    {
        A = "ERROR: Not connected to Tekla Structures. Open a model in Tekla first.";
        return;
    }

    var log = new StringBuilder();

    // ------------------------------------------------------------------
    // 1. Base slab — horizontal ContourPlate
    //    Contour at z (bottom face); plate grows upward (ABOVE).
    // ------------------------------------------------------------------
    var basePoints = new[]
    {
        new Point(x,         y,         z),
        new Point(x + B,     y,         z),
        new Point(x + B,     y + L,     z),
        new Point(x,         y + L,     z),
    };

    var basePlate = CreateContourPlate(
        profileStr : string.Format("PL{0}", (int)t_base),
        material   : mat,
        prefix     : pfx,
        name       : "BASE_SLAB",
        cls        : "1",
        points     : basePoints,
        depthEnum  : Position.DepthEnum.ABOVE);

    log.AppendLine("Base slab : " + (basePlate != null ? "OK" : "FAILED"));

    // ------------------------------------------------------------------
    // 2. Stem wall — vertical ContourPlate
    //    Contour on the front face of the stem (x = x + toe);
    //    plate grows toward the heel side (BEHIND).
    // ------------------------------------------------------------------
    double stemX    = x + toe;
    double stemZBot = z + t_base;
    double stemZTop = z + t_base + H;

    var stemPoints = new[]
    {
        new Point(stemX, y,         stemZBot),
        new Point(stemX, y + L,     stemZBot),
        new Point(stemX, y + L,     stemZTop),
        new Point(stemX, y,         stemZTop),
    };

    var stemPlate = CreateContourPlate(
        profileStr : string.Format("PL{0}", (int)t_stem),
        material   : mat,
        prefix     : pfx,
        name       : "STEM",
        cls        : "2",
        points     : stemPoints,
        depthEnum  : Position.DepthEnum.BEHIND);

    log.AppendLine("Stem      : " + (stemPlate != null ? "OK" : "FAILED"));

    // Commit all inserted objects to the model at once
    model.CommitChanges();

    A = log.ToString().TrimEnd();
}

// ---------------------------------------------------------------------------
// Helper — create and insert a ContourPlate
// ---------------------------------------------------------------------------
private ContourPlate CreateContourPlate(
    string profileStr,
    string material,
    string prefix,
    string name,
    string cls,
    Point[] points,
    Position.DepthEnum depthEnum)
{
    var plate = new ContourPlate();
    plate.Profile.ProfileString  = profileStr;
    plate.Material.MaterialString = material;
    plate.PartNumber.Prefix      = prefix;
    plate.Name                   = name;
    plate.Class                  = cls;
    plate.Position.Depth         = depthEnum;

    var contour = new Contour();
    foreach (var pt in points)
        contour.AddContourPoint(new ContourPoint(pt, null));
    plate.Contour = contour;

    return plate.Insert() ? plate : null;
}
