# Retaining Wall — Grasshopper + Tekla Structures Automation

Automated retaining wall modelling in **Tekla Structures** driven by
**Rhinoceros / Grasshopper** script components.

---

## Overview

The scripts in this repository are designed to be pasted directly into a
Grasshopper **Python Script** (GhPython) or **C# Script** component.  
On execution they call the **Tekla Open API** to create the two main
structural elements of a reinforced-concrete retaining wall:

| Element | Tekla object | Profile |
|---------|-------------|---------|
| Base slab (footing) | `ContourPlate` | `PL<t_base>` |
| Stem wall | `ContourPlate` | `PL<t_stem>` |

---

## Wall geometry

```
Cross-section (looking along +Y / wall length direction)

      +----------+
      |   STEM   |  ← height H, thickness t_stem
      |          |
------+----------+-----------
|          BASE SLAB         |  ← thickness t_base, total width B
+----------------------------+
 <── toe ──><t_stem><─ heel ─>
 <──────────── B ────────────>
```

**Coordinate system used by the scripts**

| Axis | Direction |
|------|-----------|
| X | Base width (toe → heel) |
| Y | Wall length |
| Z | Vertical (upward) |

The **origin** `(x, y, z)` is placed at the bottom-left-front corner of the
base slab.

---

## Requirements

| Software | Version |
|----------|---------|
| Rhinoceros | 7 or later |
| Grasshopper | bundled with Rhino 7+ |
| Tekla Structures | 2020 or later (must be open with an active model) |
| Tekla Open API DLLs | shipped with Tekla Structures |

The Tekla Open API DLLs are usually located at:

```
C:\Program Files\Tekla Structures\<version>\bin\
  Tekla.Structures.Model.dll
  Tekla.Structures.Geometry3d.dll
```

---

## Files

```
scripts/
  GH_RetainingWall.py   ← Grasshopper Python Script component
  GH_RetainingWall.cs   ← Grasshopper C# Script component (alternative)
```

---

## Quick-start

### Python Script component (GhPython)

1. In Grasshopper, add a **Python Script** component
   (*Maths → Script → Python Script*).
2. Right-click the component → **Edit** — paste the contents of
   `scripts/GH_RetainingWall.py`.
3. Add the inputs listed in the table below by right-clicking the component
   and choosing **Manage inputs**.
4. Connect sliders / panels to the inputs.
5. Set **`run`** to `True` to create the elements in Tekla.

### C# Script component

1. In Grasshopper, add a **C# Script** component
   (*Maths → Script → C# Script*).
2. Open the editor and paste the contents of `scripts/GH_RetainingWall.cs`.
3. In the **References** tab of the editor, add `Tekla.Structures.Model.dll`
   and `Tekla.Structures.Geometry3d.dll`.
4. Add the same inputs as described above.
5. The single output `A` will show the creation status.

---

## Input parameters

| Name | Type | Unit | Description |
|------|------|------|-------------|
| `run` | bool | — | Toggle to `True` to execute |
| `x` | float | mm | X origin (bottom-left of base slab) |
| `y` | float | mm | Y origin |
| `z` | float | mm | Z of base slab bottom |
| `L` | float | mm | Wall length (along Y) |
| `H` | float | mm | Stem height above base slab |
| `B` | float | mm | Total base width |
| `t_stem` | float | mm | Stem wall thickness |
| `t_base` | float | mm | Base slab thickness |
| `toe` | float | mm | Toe length (base left edge → stem front face) |
| `mat` | string | — | Tekla material name, e.g. `C30` |
| `pfx` | string | — | Part number prefix, e.g. `RW` |

### Typical values

| Parameter | Example value |
|-----------|--------------|
| `L` | 5000 mm |
| `H` | 3000 mm |
| `B` | 2400 mm |
| `t_stem` | 300 mm |
| `t_base` | 400 mm |
| `toe` | 600 mm |
| `mat` | `C30` |
| `pfx` | `RW` |

---

## Output

Both scripts return a status string for each created element, e.g.:

```
Base slab : OK
Stem      : OK
```

If an element fails to insert the status shows `FAILED` and you should check
the Tekla error log for details.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Not connected to Tekla Structures` | Tekla is not running or no model is open | Open a model in Tekla first |
| `FAILED` on insert | Invalid profile / material string | Check that the material name matches a Tekla catalogue entry |
| DLL not found | Tekla Open API not on PATH | Use `clr.AddReferenceToFileAndPath(...)` with the full DLL path |