// P5 CFD: builds the outer-shape part for Flow Simulation from a JSON written by cfd_geom.py (one merged solid).
// Feature kinds: "extrude" (Front-plane loops, +Z from z0 by depth), "cut_top" (Top-plane loops, cut through all
// both ways), "cyl_x" (circle on a plane at X = x0, extruded along +X). Saves the part and PNG views.
// Compiled at run time by run_cfd.ps1 (PowerShell Add-Type) against the SolidWorks interop assemblies.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

public static class SwCfdGeom
{
    static double D(object o) { return Convert.ToDouble(o); }
    static Dictionary<string, object> M(object o) { return (Dictionary<string, object>)o; }
    static IList A(object o) { return (IList)o; }

    static Feature Plane(ModelDoc2 doc, int k)          // 0 Front, 1 Top, 2 Right
    {
        int n = 0; Feature f = (Feature)doc.FirstFeature();
        while (f != null) { if (f.GetTypeName2() == "RefPlane") { if (n == k) return f; n++; } f = (Feature)f.GetNextFeature(); }
        return null;
    }

    static void Loops(ModelDoc2 doc, IList loops)
    {
        foreach (object lo in loops)
        {
            var pts = A(lo);
            for (int i = 0; i < pts.Count; i++)
            {
                var p = A(pts[i]); var q = A(pts[(i + 1) % pts.Count]);
                doc.SketchManager.CreateLine(D(p[0]) / 1000, D(p[1]) / 1000, 0, D(q[0]) / 1000, D(q[1]) / 1000, 0);
            }
        }
    }

    public static string Run(string jsonPath)
    {
        var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
        var C = M(js.DeserializeObject(File.ReadAllText(jsonPath)));
        var log = new System.Text.StringBuilder();
        var sw = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
        string partPath = (string)C["part"];
        sw.CloseDoc(Path.GetFileName(partPath));
        if (File.Exists(partPath)) File.Delete(partPath);
        string tpl = sw.GetUserPreferenceStringValue((int)swUserPreferenceStringValue_e.swDefaultTemplatePart);
        var doc = (ModelDoc2)sw.NewDocument(tpl, 0, 0, 0);
        var part = (PartDoc)doc;
        doc.SketchManager.AddToDB = true;
        foreach (object bo in A(C["bodies"]))
        {
            var b = M(bo); string kind = (string)b["kind"], name = (string)b["name"];
            Feature feat = null;
            if (kind == "extrude")
            {
                Plane(doc, 0).Select2(false, 0);
                doc.SketchManager.InsertSketch(true);
                Loops(doc, A(b["loops"]));
                double z0 = b.ContainsKey("z0") ? D(b["z0"]) : 0.0;
                feat = doc.FeatureManager.FeatureExtrusion3(true, false, false, 0, 0, D(b["depth"]) / 1000, 0, false, false,
                    false, false, 0, 0, false, false, false, false, true, true, true,
                    z0 != 0 ? (int)swStartConditions_e.swStartOffset : 0, Math.Abs(z0) / 1000, z0 < 0);
            }
            else if (kind == "cut_top")
            {
                Plane(doc, 1).Select2(false, 0);
                doc.SketchManager.InsertSketch(true);
                Loops(doc, A(b["loops"]));
                feat = doc.FeatureManager.FeatureCut4(false, false, false, (int)swEndConditions_e.swEndCondThroughAll,
                    (int)swEndConditions_e.swEndCondThroughAll, 0.01, 0.01, false, false, false, false, 0, 0, false, false,
                    false, false, false, true, true, true, true, false, 0, 0, false, false);
            }
            else if (kind == "cyl_x")
            {
                Plane(doc, 2).Select2(false, 0);
                var pl = (RefPlane)doc.FeatureManager.InsertRefPlane((int)swRefPlaneReferenceConstraints_e.swRefPlaneReferenceConstraint_Distance,
                    D(b["x0"]) / 1000, 0, 0, 0, 0);
                ((Feature)pl).Select2(false, 0);
                doc.SketchManager.InsertSketch(true);
                // Right-plane sketch: sketch x = -model Z, sketch y = model Y
                doc.SketchManager.CreateCircleByRadius(-D(b["z"]) / 1000, D(b["y"]) / 1000, 0, D(b["r"]) / 1000);
                feat = doc.FeatureManager.FeatureExtrusion3(true, false, false, 0, 0, D(b["length"]) / 1000, 0, false, false,
                    false, false, 0, 0, false, false, false, false, true, true, true, 0, 0, false);
            }
            log.AppendLine(string.Format("{0} {1}: {2}", kind, name, feat == null ? "FAILED" : "ok"));
        }
        doc.SketchManager.AddToDB = false;
        doc.ForceRebuild3(false);
        var bodies = (object[])part.GetBodies2((int)swBodyType_e.swSolidBody, true);
        var res = new Dictionary<string, object>();
        var bl = new List<object>();
        foreach (object o in bodies)
        {
            var bd = (Body2)o; var bx = (double[])bd.GetBodyBox();
            var mp = (double[])bd.GetMassProperties(1.0);
            log.AppendLine(string.Format("body {0}: X {1:F1}..{2:F1} Y {3:F1}..{4:F1} Z {5:F1}..{6:F1}, volume {7:F0} cm3", bd.Name,
                bx[0] * 1000, bx[3] * 1000, bx[1] * 1000, bx[4] * 1000, bx[2] * 1000, bx[5] * 1000, mp[3] * 1e6));
            bl.Add(new double[] { bx[0], bx[1], bx[2], bx[3], bx[4], bx[5] });
        }
        res["bodies"] = bl;
        int e1 = 0, w1 = 0;
        doc.Extension.SaveAs3(partPath, 0, 1, null, null, ref e1, ref w1);
        doc.SetUserPreferenceToggle((int)swUserPreferenceToggle_e.swDisplayPlanes, false);
        doc.SetUserPreferenceToggle((int)swUserPreferenceToggle_e.swDisplayOrigins, false);
        doc.GraphicsRedraw2();
        string stem = partPath.Replace(".SLDPRT", "");
        foreach (var v in new[] { "*Isometric", "*Top", "*Front" })
        {
            doc.ShowNamedView2(v, -1); doc.ViewZoomtofit2();
            doc.Extension.SaveAs3(stem + "_" + v.TrimStart('*').ToLower() + ".png", 0, 1, null, null, ref e1, ref w1);
        }
        res["log"] = log.ToString();
        File.WriteAllText(stem + "_geom.json", js.Serialize(res));
        return log.ToString();
    }
}
