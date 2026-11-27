// P4 tool evaluation: SolidWorks Simulation driven from the API (no GUI clicks). A balsa cantilever 100 x 10 x 3 mm,
// fixed at x = 0, a total normal force W on the whole top face (uniform line load). Linear static, solid mesh.
// Hand solution: tip deflection W L^3 / (8 E I), root bending stress (W L / 2) c / I.
// Built and run by run_sw_bench.ps1 (Windows PowerShell 5.1, Add-Type with the SolidWorks interop assemblies).
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidWorks.Interop.cosworks;

public static class SwFeaBench
{
    public static string Run(string partPath, double L_mm, double b_mm, double t_mm, double E_Pa, double W_N, double h_mm)
    {
        var log = new System.Text.StringBuilder();
        var sw = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
        string tpl = sw.GetUserPreferenceStringValue((int)swUserPreferenceStringValue_e.swDefaultTemplatePart);
        var doc = (ModelDoc2)sw.NewDocument(tpl, 0, 0, 0);
        // the default Top Plane is the 3rd plane feature; select it by type to stay independent of the UI language
        Feature f = (Feature)doc.FirstFeature();
        int nPlane = 0; Feature top = null;
        while (f != null) { if (f.GetTypeName2() == "RefPlane") { nPlane++; if (nPlane == 2) { top = f; break; } } f = (Feature)f.GetNextFeature(); }
        top.Select2(false, 0);
        doc.SketchManager.InsertSketch(true);
        doc.SketchManager.CreateCornerRectangle(0, 0, 0, L_mm / 1000.0, b_mm / 1000.0, 0);
        doc.FeatureManager.FeatureExtrusion3(true, false, false, 0, 0, t_mm / 1000.0, 0, false, false, false, false, 0, 0,
            false, false, false, false, true, true, true, 0, 0, false);
        int e1 = 0, w1 = 0;
        doc.Extension.SaveAs3(partPath, 0, 1, null, null, ref e1, ref w1);
        log.AppendLine("part saved: " + partPath + " err " + e1);

        var addin = (CwAddincallback)sw.GetAddInObject("SldWorks.Simulation");
        CosmosWorks cw = addin.CosmosWorks;
        CWModelDoc adoc = cw.ActiveDoc;
        int err;
        CWStudy study = adoc.StudyManager.CreateNewStudy3("Bench", (int)swsAnalysisStudyType_e.swsAnalysisStudyTypeStatic,
            (int)swsMeshType_e.swsMeshTypeSolid, out err);
        log.AppendLine("study err " + err);
        CWSolidBody sb = study.SolidManager.GetComponentAt(0, out err).GetSolidBodyAt(0, out err);
        CWMaterial mat = sb.GetDefaultMaterial();
        mat.MaterialUnits = 0;
        mat.MaterialName = "Balsa (design, rho 0.12)";
        mat.SetPropertyByName("EX", E_Pa, 0);
        mat.SetPropertyByName("NUXY", 0.3, 0);
        mat.SetPropertyByName("GXY", E_Pa / 2.6, 0);
        mat.SetPropertyByName("DENS", 120.0, 0);
        log.AppendLine("material err " + sb.SetSolidBodyMaterial(mat));

        // faces of the body: fixed face x = 0, loaded face = top (max z of the extrusion = thickness direction)
        var part = (PartDoc)doc;
        var body = (Body2)((object[])part.GetBodies2((int)swBodyType_e.swSolidBody, true))[0];
        Face2 fix = null, topFace = null;
        double aLb = L_mm * b_mm * 1e-6, best = double.NegativeInfinity;
        foreach (object o in (object[])body.GetFaces())
        {
            var fc = (Face2)o; var bx = (double[])fc.GetBox();
            if (Math.Abs(bx[0]) < 1e-7 && Math.Abs(bx[3]) < 1e-7) fix = fc;                      // the face at x = 0
            if (Math.Abs(fc.GetArea() - aLb) < 1e-3 * aLb)                                      // the two L x b faces
            {
                var n = (double[])fc.Normal;                                                    // outward normal
                double c = n[0] * (bx[0] + bx[3]) + n[1] * (bx[1] + bx[4]) + n[2] * (bx[2] + bx[5]);
                if (c > best) { best = c; topFace = fc; }                                        // the extruded (outer) face
            }
        }
        log.AppendLine("faces: fixed " + (fix != null) + ", loaded " + (topFace != null));
        var lbc = study.LoadsAndRestraintsManager;
        lbc.AddRestraint((int)swsRestraintType_e.swsRestraintTypeFixed, new object[] { fix }, null, out err);
        log.AppendLine("fixture err " + err);
        CWForce force = lbc.AddForce2((int)swsForceType_e.swsForceTypeNormal, (int)swsSelectionType_e.swsSelectionFaceEdgeVertexPoint,
            new object[] { topFace }, null, out err);
        log.AppendLine("force err " + err);
        force.ForceBeginEdit();
        force.NormalForceOrTorqueValue = W_N;
        force.Unit = 0;
        log.AppendLine("force end " + force.ForceEndEdit());

        CWMesh mesh = study.Mesh;
        mesh.Quality = 1;                 // high (2nd-order tetrahedra)
        int me = study.CreateMesh(0, h_mm, h_mm * 0.05);
        log.AppendLine(string.Format("mesh err {0}, nodes {1}, elements {2}", me, mesh.NodeCount, mesh.ElementCount));
        var t0 = DateTime.Now;
        int re = study.RunAnalysis();
        log.AppendLine(string.Format("run err {0} in {1:F1} s", re, (DateTime.Now - t0).TotalSeconds));
        CWResults res = study.Results;
        if (res != null)
        {
            var d = (object[])res.GetMinMaxDisplacement((int)swsDisplacementComponent_e.swsDisplacementComponentURES, 1, null,
                (int)swsLinearUnit_e.swsLinearUnitMillimeters, out err);
            var s = (object[])res.GetMinMaxStress((int)swsStressComponent_e.swsStressComponentSX, 0, 1, null,
                (int)swsStrengthUnit_e.swsStrengthUnitNewtonPerSquareMillimeter, out err);
            log.AppendLine(string.Format("RESULT max URES {0:F4} mm; SX min {1:F4} max {2:F4} N/mm2",
                Convert.ToDouble(d[3]), Convert.ToDouble(s[1]), Convert.ToDouble(s[3])));
        }
        else log.AppendLine("no results");
        return log.ToString();
    }
}
