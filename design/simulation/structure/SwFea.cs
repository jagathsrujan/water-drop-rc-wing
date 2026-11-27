// P6: general SOLIDWORKS Simulation driver. A JSON case file (written by Python from the rev B part data) gives the
// bodies (outline loops on the Front plane, extruded along +Z from a start offset), their materials (isotropic or
// orthotropic in the global axes), fixtures, loads, mesh and the probes to report; the driver builds the part,
// the static study, meshes, solves and writes <case>_result.json and PNG plots. Compiled at run time by
// run_fea.ps1 (Windows PowerShell 5.1 Add-Type) against the SolidWorks interop assemblies.
// Face rules: {"body": name or "*", "at": [axis, value_mm]} = planar faces lying on that coordinate plane;
//             {"body": name, "extreme": [axis, "max"|"min"]} = the planar face(s) normal to that axis furthest out.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidWorks.Interop.cosworks;

public static class SwFea
{
    static double D(object o) { return Convert.ToDouble(o); }
    static Dictionary<string, object> M(object o) { return (Dictionary<string, object>)o; }
    static IList A(object o) { return (IList)o; }

    public static string Run(string casePath)
    {
        var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
        var C = M(js.DeserializeObject(File.ReadAllText(casePath)));
        var log = new System.Text.StringBuilder();
        var res = new Dictionary<string, object>();
        var sw = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
        sw.CloseDoc(Path.GetFileName((string)C["part"]));          // an earlier run of this case still open
        if (File.Exists((string)C["part"])) File.Delete((string)C["part"]);
        string tpl = sw.GetUserPreferenceStringValue((int)swUserPreferenceStringValue_e.swDefaultTemplatePart);
        var doc = (ModelDoc2)sw.NewDocument(tpl, 0, 0, 0);
        Feature front = null; Feature f = (Feature)doc.FirstFeature();
        while (f != null) { if (f.GetTypeName2() == "RefPlane") { front = f; break; } f = (Feature)f.GetNextFeature(); }
        var part = (PartDoc)doc;
        var names = new List<string>();
        doc.SketchManager.AddToDB = true;
        foreach (object bo in A(C["bodies"]))
        {
            var b = M(bo);
            front.Select2(false, 0);
            doc.SketchManager.InsertSketch(true);
            foreach (object lo in A(b["loops"]))
            {
                var pts = A(lo);
                for (int i = 0; i < pts.Count; i++)
                {
                    var p = A(pts[i]); var q = A(pts[(i + 1) % pts.Count]);
                    doc.SketchManager.CreateLine(D(p[0]) / 1000, D(p[1]) / 1000, 0, D(q[0]) / 1000, D(q[1]) / 1000, 0);
                }
            }
            if (b.ContainsKey("circles"))
                foreach (object co in A(b["circles"]))
                {
                    var c = A(co);
                    doc.SketchManager.CreateCircleByRadius(D(c[0]) / 1000, D(c[1]) / 1000, 0, D(c[2]) / 1000);
                }
            double z0 = b.ContainsKey("z0") ? D(b["z0"]) : 0.0;
            var feat = doc.FeatureManager.FeatureExtrusion3(true, false, false, 0, 0, D(b["depth"]) / 1000, 0, false, false,
                false, false, 0, 0, false, false, false, false, false, true, true,
                z0 != 0 ? (int)swStartConditions_e.swStartOffset : 0, Math.Abs(z0) / 1000, z0 < 0);
            if (feat == null) { log.AppendLine("EXTRUDE FAILED " + b["name"]); continue; }
            var bodies = (object[])part.GetBodies2((int)swBodyType_e.swSolidBody, true);
            foreach (object o in bodies)
            {
                var bd = (Body2)o;
                if (!names.Contains(bd.Name) && (bd.Name.StartsWith("Boss-Extrude") || bd.Name.StartsWith("Extrude")))
                { bd.Name = (string)b["name"]; break; }
            }
            names.Add((string)b["name"]);
        }
        doc.SketchManager.AddToDB = false;
        doc.ForceRebuild3(false);
        int e1 = 0, w1 = 0;
        doc.Extension.SaveAs3((string)C["part"], 0, 1, null, null, ref e1, ref w1);
        var allBodies = new Dictionary<string, Body2>();
        foreach (object o in (object[])part.GetBodies2((int)swBodyType_e.swSolidBody, true))
        {
            var bd = (Body2)o; allBodies[bd.Name] = bd;
            var bx = (double[])bd.GetBodyBox();
            log.AppendLine(string.Format("body {0}: x {1:F1}..{2:F1} y {3:F1}..{4:F1} z {5:F1}..{6:F1}", bd.Name,
                bx[0] * 1000, bx[3] * 1000, bx[1] * 1000, bx[4] * 1000, bx[2] * 1000, bx[5] * 1000));
        }

        var addin = (CwAddincallback)sw.GetAddInObject("SldWorks.Simulation");
        if (addin == null)
        {
            sw.LoadAddIn(@"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.dll");
            addin = (CwAddincallback)sw.GetAddInObject("SldWorks.Simulation");
        }
        CosmosWorks cw = addin.CosmosWorks;
        CWModelDoc adoc = cw.ActiveDoc;
        int err;
        CWStudy study = adoc.StudyManager.CreateNewStudy3((string)C["name"], 0, 0, out err);
        // materials, per body by name
        var comp = study.SolidManager.GetComponentAt(0, out err);
        for (int i = 0; i < comp.SolidBodyCount; i++)
        {
            var sb = comp.GetSolidBodyAt(i, out err);
            string bn = sb.SolidBodyName;                          // "SolidBody 3(WEB-R)" -> "WEB-R"
            int ia = bn.LastIndexOf('('), ib = bn.LastIndexOf(')');
            if (ia >= 0 && ib > ia) bn = bn.Substring(ia + 1, ib - ia - 1);
            Dictionary<string, object> bdef = null;
            foreach (object bo in A(C["bodies"])) if ((string)M(bo)["name"] == bn) bdef = M(bo);
            if (bdef == null) { log.AppendLine("no definition for body " + bn); continue; }
            var md = M(bdef["material"]);
            CWMaterial mat = sb.GetDefaultMaterial();
            mat.MaterialUnits = 0;
            mat.MaterialName = (string)md["name"];
            if ((string)md["model"] == "ortho")
            {
                mat.ModelType = (int)swsMaterialModelType_e.swsMaterialModelTypeLinearElasticOrthtropic;
                foreach (var k in new[] { "EX", "EY", "EZ", "NUXY", "NUYZ", "NUXZ", "GXY", "GYZ", "GXZ" })
                    mat.SetPropertyByName(k, D(md[k]), 0);
            }
            else
            {
                mat.ModelType = 0;
                mat.SetPropertyByName("EX", D(md["E"]), 0);
                mat.SetPropertyByName("NUXY", D(md["nu"]), 0);
                mat.SetPropertyByName("GXY", D(md["E"]) / (2 * (1 + D(md["nu"]))), 0);
            }
            mat.SetPropertyByName("DENS", D(md["rho"]), 0);
            int me = sb.SetSolidBodyMaterial(mat);
            log.AppendLine("material " + bn + " -> " + md["name"] + " err " + me);
        }
        var lbc = study.LoadsAndRestraintsManager;
        foreach (object fo in A(C["fixtures"]))
        {
            var fx = M(fo);
            var faces = SelectFaces(allBodies, A(fx["faces"]));
            lbc.AddRestraint((int)swsRestraintType_e.swsRestraintTypeFixed, faces.ToArray(), null, out err);
            log.AppendLine("fixture on " + faces.Count + " faces, err " + err);
        }
        foreach (object lo in A(C["loads"]))
        {
            var ld = M(lo);
            var faces = SelectFaces(allBodies, A(ld["faces"]));
            CWForce force = lbc.AddForce2((int)swsForceType_e.swsForceTypeNormal, 0, faces.ToArray(), null, out err);
            force.ForceBeginEdit();
            force.NormalForceOrTorqueValue = D(ld["total_N"]);
            force.Unit = 0;
            int fe = force.ForceEndEdit();
            log.AppendLine(string.Format("normal force {0} N on {1} faces, err {2}/{3}", ld["total_N"], faces.Count, err, fe));
        }
        var ms = M(C["mesh"]);
        CWMesh mesh = study.Mesh;
        mesh.Quality = 1;
        int mr = study.CreateMesh(0, D(ms["size"]), D(ms["size"]) * 0.05);
        log.AppendLine(string.Format("mesh {0} mm: err {1}, nodes {2}, elements {3}", ms["size"], mr, mesh.NodeCount, mesh.ElementCount));
        res["nodes"] = mesh.NodeCount; res["elements"] = mesh.ElementCount;
        var t0 = DateTime.Now;
        int rr = study.RunAnalysis();
        res["solve_s"] = (DateTime.Now - t0).TotalSeconds;
        log.AppendLine(string.Format("run err {0} in {1:F1} s", rr, res["solve_s"]));
        CWResults R = study.Results;
        if (R == null) { log.AppendLine("NO RESULTS"); res["log"] = log.ToString(); return Save(js, C, res); }
        res["log"] = log.ToString(); Save(js, C, res);          // keep what we have if post-processing fails
        try { var d = (object[])R.GetMinMaxDisplacement(3, 1, null, 0, out err); res["URES_max_mm"] = D(d[3]); }
        catch (Exception ex) { log.AppendLine("URES failed: " + ex.Message); }
        var probes = new List<object>();
        foreach (object po in A(C["probes"]))
        {
            var pr = M(po);
            var faces = SelectFaces(allBodies, A(pr["faces"]));
            var pv = new Dictionary<string, object>(); pv["label"] = pr["label"];
            try {
            if ((string)pr["kind"] == "stress")
            {
                var v = (object[])R.GetStressForEntities2(true, Convert.ToInt32(pr["component"]), 1, null, faces.ToArray(), 3, out err);
                if (v != null && v.Length > 1) { var vals = Pairs(v); pv["min"] = Min(vals); pv["max"] = Max(vals); pv["n"] = vals.Length; }
                pv["err"] = err;
            }
            else
            {
                var v = (object[])R.GetDisplacementForEntities(Convert.ToInt32(pr["component"]), 1, null, faces.ToArray(), 0, out err);
                if (v != null && v.Length > 1) { var vals = Pairs(v); pv["min"] = Min(vals); pv["max"] = Max(vals); pv["n"] = vals.Length; }
                pv["err"] = err;
            }
            } catch (Exception ex) { pv["error"] = ex.Message; }
            probes.Add(pv);
            res["probes"] = probes; res["log"] = log.ToString(); Save(js, C, res);
            log.AppendLine(string.Format("probe {0}: {1} .. {2}", pr["label"], pv.ContainsKey("min") ? pv["min"] : "-", pv.ContainsKey("max") ? pv["max"] : "-"));
        }
        res["probes"] = probes;
        // plots: the default stress and displacement plots, isometric, saved as PNG next to the case file
        var imgs = new List<object>();
        string dir = Path.GetDirectoryName(casePath), cname = (string)C["name"];
        string[] plotNames = new string[0];
        try { plotNames = (string[])R.GetPlotNames(); } catch (Exception ex) { log.AppendLine("plots: " + ex.Message); }
        if (C.ContainsKey("images") && !(bool)C["images"]) plotNames = new string[0];
        foreach (string pn in plotNames)
        {
          try {
            R.ActivatePlot(pn);
            doc.ShowNamedView2("*Isometric", 7);
            doc.ViewZoomtofit2();
            string png = Path.Combine(dir, cname + "_" + pn + ".png");
            doc.Extension.SaveAs3(png, 0, 1, null, null, ref e1, ref w1);
            imgs.Add(png);
          } catch (Exception ex) { log.AppendLine("image " + pn + ": " + ex.Message); }
        }
        res["images"] = imgs;
        res["log"] = log.ToString();
        doc.Save3(1, ref e1, ref w1);
        return Save(js, C, res);
    }

    static string Save(JavaScriptSerializer js, Dictionary<string, object> C, Dictionary<string, object> res)
    {
        string outp = ((string)C["part"]).Replace(".SLDPRT", "_result.json");
        File.WriteAllText(outp, js.Serialize(res));
        return (string)res["log"];
    }

    // the ...ForEntities calls return (node number, value) pairs
    static double[] Pairs(object[] v)
    {
        var o = new double[v.Length / 2];
        for (int i = 0; i < o.Length; i++) o[i] = D(v[2 * i + 1]);
        return o;
    }

    static double Min(double[] v) { double m = double.MaxValue; foreach (var x in v) m = Math.Min(m, x); return m; }
    static double Max(double[] v) { double m = double.MinValue; foreach (var x in v) m = Math.Max(m, x); return m; }

    static List<object> SelectFaces(Dictionary<string, Body2> bodies, IList rules)
    {
        var outl = new List<object>();
        foreach (object ro in rules)
        {
            var r = M(ro);
            string bn = (string)r["body"];
            foreach (var kv in bodies)
            {
                if (bn != "*" && kv.Key != bn) continue;
                Face2 best = null; double bestc = 0; var bests = new List<Face2>();
                foreach (object fo in (object[])kv.Value.GetFaces())
                {
                    var fc = (Face2)fo; var bx = (double[])fc.GetBox();
                    if (r.ContainsKey("all")) { outl.Add(fc); continue; }
                    if (r.ContainsKey("at"))
                    {
                        var at = A(r["at"]); int ax = Convert.ToInt32(at[0]); double v = D(at[1]) / 1000;
                        if (Math.Abs(bx[ax] - v) < 2e-6 && Math.Abs(bx[ax + 3] - v) < 2e-6) outl.Add(fc);
                    }
                    else if (r.ContainsKey("extreme"))
                    {
                        var ex = A(r["extreme"]); int ax = Convert.ToInt32(ex[0]); bool mx = (string)ex[1] == "max";
                        if (Math.Abs(bx[ax] - bx[ax + 3]) > 2e-6) continue;          // not a plane normal to ax
                        double c = bx[ax];
                        if (best == null || (mx ? c > bestc + 1e-7 : c < bestc - 1e-7)) { best = fc; bestc = c; bests.Clear(); bests.Add(fc); }
                        else if (Math.Abs(c - bestc) < 1e-7) bests.Add(fc);
                    }
                }
                foreach (var b in bests) outl.Add(b);
            }
        }
        return outl;
    }
}
