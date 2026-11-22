"""Video script: segments (id, kind, title, narration). Writes narration.json and audio/<id>.aiff with macOS `say`.
kind: card | orbit | step (FreeCAD) | laser | glue | cover | tools."""
import json, os, subprocess
VOICE, RATE = "Aman", 172
S = [
 ("00_intro", "card", "Water-drop RC aircraft — balsa wing, rev A",
  "This video shows how to build the balsa wing of our water-drop aircraft for the Boeing National Aeromodelling Competition. "
  "The wing has a span of 990 millimetres, a chord of 280 millimetres and an S D 7062 airfoil, and it weighs about 157 grams without servos. "
  "All files, the bill of materials with Indian shop links, and notes on what to ask for in local shops are on the project web page and on GitHub. "
  "You will find the links at the end of this video."),
 ("01_overview", "orbit", "The complete wing",
  "Here is the complete wing. It is a classic built-up structure: laser-cut ribs every 55 millimetres, a spar with carbon caps, "
  "a sheeted leading-edge D-box for torsion stiffness, a false spar that carries the aileron hinges, and 3D-printed P E T G servo mounts. "
  "Each aileron is 325 millimetres long and is driven by an M G 90 S servo."),
 ("02_materials", "materials", "Materials",
  "You will need balsa sheets in 1.5, 2, 3 and 6 millimetre thickness, four pultruded carbon strips of 3 by 0.5 millimetres, "
  "iron-on covering film, C A hinges, a 1.2 millimetre steel pushrod, P E T G filament, and two M G 90 S servos. "
  "You also need three glues: thin C A, a P V A wood glue such as Fevicol S H, and epoxy."),
 ("03_tools", "tools", "Tools",
  "For tools, you need a laser cutter or a sharp hobby knife, a flat building board at least 1.2 metres long, T-pins, a steel rule, "
  "sanding blocks, a covering iron and a heat gun, a scale that reads to 0.1 gram, and a 3D printer."),
 ("04_weigh", "weigh", "Weigh and sort the balsa",
  "Before you cut anything, weigh every balsa sheet and divide the mass by its volume to get the density. "
  "Use the lightest sheets, about 90 kilograms per cubic metre, for the sheeting, medium sheets for the ribs and webs, "
  "and the hardest sheets for the spar caps and trailing edges. This one step can save ten grams or more."),
 ("05_laser", "laser", "Laser cutting the flat parts",
  "Laser cut the ribs and the other flat parts from the D X F files. Each file is one sheet of 300 by 100 millimetres, with the grain along the long side. "
  "Cut only the layer called CUT. Make test cuts on scrap first: balsa needs low power and high speed. "
  "Keep a fire extinguisher near the machine, and never leave the laser running alone."),
 ("06_strips", "strips", "Strip stock",
  "Cut the long strips with a steel rule and a sharp knife: two spar caps of 3 by 6 millimetres from hard balsa, "
  "the 6 millimetre leading edge, the trailing-edge stock, and 6 millimetre cap strips from 1.5 millimetre sheet. The cut list gives every length."),
 ("07_glue", "glue", "Which glue goes where",
  "Three glues do three jobs. Thin C A wicks into tight joints and sets in seconds; use it for ribs, cap strips and hinges. "
  "P V A wood glue gives you time to adjust and sands easily; use it to laminate the tip ribs and to glue the sheeting. "
  "Epoxy bonds the carbon to the balsa and the printed parts to the wood. Mix equal amounts of resin and hardener, and use a thin layer. "
  "Work in fresh air, and protect your eyes and fingers from C A."),
 ("08_spar", "step", "Step 1 — Spar caps",
  "Step one. Glue two carbon strips side by side onto each balsa spar cap with a thin layer of epoxy. "
  "Put a weight on them, on a flat surface covered with plastic film, and let the epoxy cure."),
 ("09_ribs", "step", "Step 2 — Ribs on the bottom spar cap",
  "Step two. Pin the bottom spar cap on the board over the plan, with the carbon face down. "
  "Support the rib noses on a 3.5 millimetre strip and the rib tails on an 8 millimetre strip, so that every rib sits at the correct angle. "
  "Slide the ribs onto the spar cap and glue them square, with a set square. The ribs at 110 millimetres from the centre are 3 millimetres thick."),
 ("10_le_te", "step", "Step 3 — Leading edge, false spar, trailing edge",
  "Step three. Glue the leading-edge stock to the front of the ribs, then the false spar at 205 millimetres, the aft rib pieces, and the trailing-edge wedges. "
  "Keep the trailing edge straight with pins on both sides."),
 ("11_webs", "step", "Step 4 — Top spar cap and shear webs",
  "Step four. Glue the top spar cap into the rib notches with the carbon face up. "
  "Then glue the vertical-grain shear webs between the ribs: in front of the spar along the full span, and behind it near the centre. "
  "The webs make the spar into a strong box."),
 ("12_top", "step", "Step 5 — Top sheeting and cap strips",
  "Step five. Sand everything flush. Glue on the top D-box sheeting from the leading edge to 80 millimetres, then the centre sheeting and the cap strips. "
  "Wet the outer face of the sheeting lightly, so that it bends around the nose without cracking."),
 ("13_flip", "step", "Step 6 — Turn over: bottom sheeting and servo frames",
  "Step six. Remove the wing from the board and turn it over. Add the bottom D-box sheeting, the bottom centre sheeting with the wire exit holes, "
  "and the bottom cap strips. Then glue the printed servo frames between the ribs at 110 and 165 millimetres."),
 ("14_tips", "step", "Step 7 — Tip ribs and tip caps",
  "Step seven. Laminate each tip rib from two 1.5 millimetre layers with the grain crossed, and glue it on at 489 millimetres. "
  "Add the 3 millimetre ring tip cap, then sand the whole wing smooth with a long sanding block."),
 ("15_ailerons", "step", "Step 8 — Ailerons",
  "Step eight. Build each aileron from its 3 millimetre leading edge, its ribs and the trailing-edge wedge. "
  "Sand a V bevel on the leading edge so that the aileron can move 20 degrees each way. "
  "Then cut the four hinge slots in the false spar and in the aileron with a knife blade."),
 ("16_cover", "cover", "Covering",
  "Cover the wing with iron-on film. Iron the edges down first, at about 110 to 120 degrees Celsius or as the film maker says, "
  "then shrink the open areas with the heat gun. Cover the ailerons separately, and cut the film away over the hinge slots and the servo hatch."),
 ("17_servo", "servo", "Step 9 — Hinges, horns and servos",
  "Step nine. Push in the C A hinges, check that the aileron moves freely, then wick thin C A into both sides of each hinge. "
  "Glue the printed horns to the horn ribs. Screw each servo to its hatch, connect the 1.2 millimetre pushrod with Z bends, "
  "and fix the hatch with four M 2 screws."),
 ("18_final", "step", "Step 10 — Finish and check",
  "Finally, add the rubber-band rub plates at the centre, centre the servos, and set the throws to plus or minus 15 degrees. "
  "Then weigh the wing. The target is less than 160 grams without the servos."),
 ("19_checks", "checks", "Design checks",
  "Our design checks: span 990 millimetres, chord 280 millimetres, spar depth 39.2 millimetres, no overlapping parts, "
  "at least 1 millimetre of servo clearance, and a predicted mass of 157 grams."),
 ("20_outro", "outro", "Links and files",
  "Every link for the materials, with notes on what to ask for in local shops and markets, is on the web page and in the GitHub repository: "
  "github dot com, slash jagath srujan, slash water-drop R C wing. Thank you for watching, and happy building."),
]
os.makedirs("audio", exist_ok=True)
out = []
for sid, kind, title, text in S:
    a = os.path.join("audio", sid + ".aiff")
    subprocess.run(["say", "-v", VOICE, "-r", str(RATE), "-o", a, text], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a]).decode())
    out.append(dict(id=sid, kind=kind, title=title, text=text, audio=a, dur=round(dur, 3), seg=round(dur + 0.8, 3)))
    print(sid, round(dur, 1))
json.dump(out, open("narration.json", "w"), indent=1)
print("total", round(sum(o["seg"] for o in out), 1), "s")
