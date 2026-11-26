"""The build of the rev B balsa aircraft, step by step, for the build game, the printable step list and BUILD_GUIDE.md.

Each step lists what the builder does, in order. Item kinds:
  P(name)   place a part (its engraved name must exist in the part data; checked by make_build_kit.py)
  K(id)     place a group of parts that go on as one piece (e.g. a laminated side panel); members are real parts
  A(id)     an action (pins, glue, sanding, a check)
  N(id)     set a linkage to neutral (servo centred and surface at 0 deg) before the Z-bend is made
needs:      what must be done first: [(item, why)] - 'why' is one of order / jig / pin / glue / cure / safety
            and the text is the explanation shown when the builder gets it wrong.
Traps are tempting wrong actions; the game explains each one. Distractors are parts that do not belong in the step.

Geometry-based needs (which floor piece holds which former, which ribs a web sits between, which side panels a
former's tabs go through) are filled in by make_build_kit.py from the part data, not typed here."""


def P(name, needs=(), why="", slot=True, orient=True):
    return dict(kind="part", id=name, parts=[name], needs=list(needs), why=why, slot=slot, orient=orient)


def K(id_, label, members, needs=(), why="", slot=True, orient=True, hint_from=None):
    return dict(kind="group", id=id_, label=label, parts=list(members), needs=list(needs), why=why, slot=slot,
                orient=orient, hint_from=hint_from or members[0])


def A(id_, label, needs=(), why=""):
    return dict(kind="action", id=id_, label=label, needs=list(needs), why=why)


def N(id_, label, surface, needs=(), why=""):
    return dict(kind="neutral", id=id_, label=label, surface=surface, needs=list(needs), why=why)


def T(id_, label, mistake, fix, kind="trap"):
    """A tempting wrong action. kind: trap / glue-gap / order / neutral / safety (the mistake type in the log)."""
    return dict(id=id_, label=label, mistake=mistake, fix=fix, type=kind)


R_OUT = ["RO-NL", "RO-NU", "RO-M1L", "RO-M1U", "RO-MP", "RO-M3L", "RO-M3U", "RO-TL", "RO-TU"]
R_IN = ["RI-N1", "RI-N2", "RI-M1", "RI-M2U", "RI-M2G", "RI-M3U", "RI-M3G", "RI-M4", "RI-M5", "RI-T1"]
L_OUT = ["LO-NL", "LO-NU", "LO-ML", "LO-MU", "LO-TL", "LO-TU"]
L_IN = ["LI-N1", "LI-N2", "LI-M1", "LI-M2U", "LI-M2G", "LI-M3U", "LI-M4", "LI-M5", "LI-T1"]
FORMERS = ["N1", "N2", "FS", "B1", "B2-R", "B2-L", "B4", "BH", "EF"]
RIB_Y = ["055", "110", "165", "220", "275", "330", "385", "440"]
RIBS = ["W-C"] + ["W-R%s-%s" % (y, s) for s in "RL" for y in RIB_Y] + ["W-TIP-R", "W-TIP-L"]
WEBS = ["WF-%s%d" % (s, i) for s in "RL" for i in range(1, 10)] + ["WR-%s%d" % (s, i) for s in "RL" for i in range(1, 4)] +     ["WF-R1D", "WF-L1D"]                   # P2 item 11: root-bay web doublers
CAPS_STATIONS = ["R110", "R165", "R220", "R275", "R330", "R385", "R440", "TIP"]


def caps(side, face, names):
    """Cap strips of one side and face (T / B) that exist in the part data."""
    out = []
    for st in CAPS_STATIONS:
        for fa in ("F", "A"):
            n = "CAPS-%s-%s%s-%s" % (st, face, fa, side)
            if n in names:
                out.append(n)
    return out


def ail(side):
    return ["AIL-LE-" + side] + ["A%s-%s" % (y, side) for y in ("112", "165", "220", "275", "330", "385", "437")] + \
           ["AH-" + side, "AIL-TE-" + side]


def laminate(side, outer, inner, doubler):
    S = {"R": "right", "L": "left"}[side]
    other = {"R": "left", "L": "right"}[side]
    items = [A("wax-" + side, "Lay wax paper (or cling film) on the flat building board",
               why="PVA squeezes out of the joints; without a release sheet the laminate sticks to the board.")]
    items += [P(n, needs=[("wax-" + side, "order", "Put the wax paper down first, or the outer layer glues itself to the board.")],
                slot=False) for n in outer]
    items.append(A("pva-" + side, "Spread a thin coat of PVA (Fevicol SH thinned about 10 % with water) over the outer layer",
                   needs=[(n, "order", "Lay every outer-layer piece first: the inner layer must bridge the outer joints.") for n in outer]))
    items += [P(n, needs=[("pva-" + side, "glue", "Spread the PVA on the outer layer before you lay the inner pieces.")],
                slot=False) for n in inner]
    items.append(P(doubler, needs=[(inner[2], "order", "The stub doubler sits on the inner layer over the band-stub hole: lay %s first." % inner[2])],
                   slot=False, why="Birch doubler (2 x 1.5 mm laminated) that carries the front rubber-band stub."))
    items.append(A("weights-" + side, "Cover with wax paper, a flat board and weights; leave it flat overnight",
                   needs=[(n, "order", "Every piece must be in place before the weights go on.") for n in inner + [doubler]]))
    return dict(
        id="laminate-" + side, phase="Pod", title="Laminate the %s side layers" % S, view="flat-" + side, mode="place",
        intro=("The %s side is two layers: an outer 1.5 mm balsa skin (grain along the pod, lower and upper strips joined at "
               "Z -40) and an inner 1.5 mm layer (grain vertical, pieces no wider than 100 mm), both from the one 1.5 mm stock. Every joint in one layer is "
               "bridged by the other layer. The nose (N), middle (M) and tail-cone (T) panels are separate: they meet at the "
               "kinks later. Lay each piece engraved face UP, arrow pointing to the nose (%s): the engraved faces end up "
               "inside the pod.") % (S, "'< FWD'" if side == "R" else "'FWD >'"),
        items=items,
        traps=[T("ca-" + side, "Glue the layers with thin CA and press them by hand",
                 "CA grabs in seconds, before the layers lie flat, and a CA laminate is hard and brittle.",
                 "Use thinned PVA under weights on a flat board: it gives you time to line the pieces up and dries flat."),
               T("grain-" + side, "Turn the inner pieces so their grain runs along the pod like the outer skin",
                 "The pieces are cut with the grain already set: outer skin along X, inner layer vertical. Turning them "
                 "puts both grains the same way and the side loses its cross-laminate stiffness.",
                 "Lay each piece as cut, with its engraved arrow to the nose.")],
        tip="Weigh every 1.5 mm sheet before cutting: the lightest go to the D-box, sheeting and tail, the heaviest to formers and the bulkhead.",
        other_side=other)


def steps(names):
    """The full build. names: set of part names in the part data (used for the cap-strip groups)."""
    S = []
    S.append(laminate("R", R_OUT, R_IN, "SD-R"))
    S.append(laminate("L", L_OUT, L_IN, "SD-L"))
    S.append(dict(id="laminate-parts", phase="Pod", title="Laminate the thick parts from 1.5 mm layers", view="pod-iso", mode="place",
                  intro="Everything is cut from one 1.5 mm stock. The thicker parts are 2-4 layers glued flat: the formers "
                        "N1, N2, B1, B2, B4 and EF (3 layers, grain crossed), the bulkhead BH (4 layers), the saddle layers, "
                        "the trays and strap bridges (2 layers), W-C, W-R110 and the false spar (2 layers), and the tail "
                        "surfaces (2 layers); in birch ply the front stop FS, firewall, stub doublers and tube rings (2 "
                        "layers, face grain crossed). Each layer piece is engraved <part>-<layer><piece> (e.g. B1-2a): "
                        "layer 1 at the bottom, the joints of the pieces of one layer are bridged by the next layer.",
                  items=[A("lam-pva", "Spread thinned PVA thinly on one face of each layer; stack the layers in number order, "
                                      "edges and holes lined up (push toothpicks or 2 mm rod through two holes)"),
                         A("lam-press", "Press flat between wax paper and boards under weights overnight; do not sand or slot "
                                        "the parts until fully dry", needs=[("lam-pva", "order", "Stack the layers first.")])],
                  traps=[T("lam-ca", "Laminate the layers with thin CA",
                           "CA sets before the layers lie flat and adds hard, heavy glue lines.",
                           "Thinned PVA, a thin even coat, rolled or brushed, then weights on a flat board.")],
                  tip="Weigh one 100 x 100 mm test laminate of 2 x 1.5 mm: the glue should add about 0.4 g (40 g/m2); "
                      "more means too much glue."))

    # ---------------------------------------------------------------- jig base
    jb = ["JB-A", "JB-B", "JB-C", "JB-D1", "JB-D2"]
    adj = {"JB-A": ["JB-B"], "JB-B": ["JB-A", "JB-C"], "JB-C": ["JB-B", "JB-D1"], "JB-D1": ["JB-C", "JB-D2"], "JB-D2": ["JB-D1"]}
    items = []
    for n in jb:
        it = P(n)
        it["needs_any"] = [adj[n], "order", "Each segment keys onto one already on the table: slide the dovetails together "
                                            "on a flat table, working from one end."]
        it["first_ok"] = True
        items.append(it)
    items.append(A("jb-ca", "Check the base lies flat on the table, then put one drop of thin CA on each dovetail key",
                   needs=[(n, "order", "Key all five segments together and check them flat before any glue.") for n in jb]))
    S.append(dict(id="jig-base", phase="Pod", title="Key the jig base together", view="pod-top", mode="slot",
                  intro="The five printed segments JB-A to JB-D2 make one 808 mm base. Its top IS the building surface "
                        "(Z -117, the underside of the bay floor). Every pod jig is located on it by two 6 mm pins, and "
                        "each jig's name is engraved where it goes. Arrows '< FWD' point to the nose.",
                  items=items,
                  traps=[T("jb-screw", "Screw the segments to the building board instead of keying them",
                           "Screws pull the thin base out of flat and the segments drift apart: the jig positions are "
                           "only right when the dovetails are fully home.",
                           "Key the dovetails on a flat table and fix each with a drop of CA.")],
                  tip="Print the base holes at 6.1 mm and the pins at 5.9 mm. A loose pin: a drop of CA in the base hole."))

    # ---------------------------------------------------------------- floor
    items = [A("pins-J1a", "Push 2 x PIN-6x11 into the base holes marked J1a (JB-A)"),
             P("J1a-NOSE-WEDGE", needs=[("pins-J1a", "pin", "J1a drops onto two pins in JB-A. Without the pins it is not where "
                                                           "the model has it, and the nose floor gets the wrong slope.")]),
             A("pins-J1b", "Push 2 x PIN-6x11 into the base holes marked J1b (JB-C)"),
             P("J1b-TAIL-WEDGE", needs=[("pins-J1b", "pin", "J1b sits on two pins in JB-C. Put the pins in first.")])]
    floor_adj = {"FL-M1": ["FL-M2"], "FL-M2": ["FL-M1", "FL-M3"], "FL-M3": ["FL-M2", "FL-M4"], "FL-M4": ["FL-M3"]}
    for n in ["FL-M1", "FL-M2", "FL-M3", "FL-M4"]:
        it = P(n)
        it["needs_any"] = [floor_adj[n], "order", "Floor pieces join with dovetail keys: each new piece keys into one already "
                                                  "on the base. Work along the bay from one piece."]
        it["first_ok"] = True
        items.append(it)
    items += [P("FL-N2", needs=[("J1a-NOSE-WEDGE", "jig", "FL-N2 lies on the J1a nose wedge, which sets the 15.5 deg nose-floor "
                                                         "slope. Pin J1a first."),
                                ("FL-M1", "order", "The nose floor meets the bay floor (FL-M1) at the kink: lay FL-M1 first.")]),
              P("FL-N1", needs=[("FL-N2", "order", "FL-N1 keys into FL-N2 with dovetails: lay FL-N2 first."),
                                ("J1a-NOSE-WEDGE", "jig", "FL-N1 lies on J1a. Pin J1a first.")]),
              P("FL-T1", needs=[("J1b-TAIL-WEDGE", "jig", "FL-T1 lies on the J1b tail wedge at the 38.6 deg tail-cone slope. Pin J1b first."),
                                ("FL-M4", "order", "The tail-cone floor meets FL-M4 at the kink: lay FL-M4 first.")]),
              P("FLAPSTOP", why="1.5 mm ply flap stop on the bay floor (D-061)."),
              A("floor-ca", "Wick thin CA into every dovetail joint (not into the former slots)",
                needs=[(n, "order", "Lay all seven floor pieces before gluing the dovetails.") for n in
                       ["FL-N1", "FL-N2", "FL-M1", "FL-M2", "FL-M3", "FL-M4", "FL-T1"]])]
    S.append(dict(id="floor", phase="Pod", title="Pin the floor wedges and lay the floor", view="pod-top", mode="slot",
                  intro="The bay floor (FL-M1 to FL-M4) lies flat on the base; the nose floor (FL-N1, FL-N2) lies on the "
                        "J1a wedge and the tail-cone floor (FL-T1) on the J1b wedge. Pieces join with dovetail keys. Each "
                        "floor piece has the names of its formers engraved beside their slots. Engraved face up, '< FWD' "
                        "to the nose.",
                  items=items,
                  traps=[T("floor-slots-ca", "Run CA into the empty former slots so they are stiff",
                           "Glue in the slots narrows them: the former tabs will not go in.",
                           "Glue the dovetails only. The slots get glue when the formers are in.", "glue-gap")]))

    # ---------------------------------------------------------------- formers
    items = [P(n) for n in FORMERS]
    items.append(P("TRAY", needs=[("N1", "order", "The battery tray's tabs go into notches in the N1 and N2 legs: N1 first."),
                                  ("N2", "order", "The battery tray's tabs go into notches in the N1 and N2 legs: N2 first.")],
                   why="Battery tray, 2 x 1.5 mm balsa laminated (grain crossed)."))
    items.append(A("formers-square", "Check each former square to the floor (set square), then wick thin CA into the floor tabs",
                   needs=[(n, "order", "Drop every former in before gluing.") for n in FORMERS]))
    S.append(dict(id="formers", phase="Pod", title="Drop the formers into their floor slots", view="pod-iso", mode="slot",
                  intro="Each former has 3 floor tabs (2 on the B2 halves and EF) that drop through the slots with its name "
                        "beside them. 'UP ^' points up. Lite-ply N1, N2, FS, B1, B2, B4, EF; birch-ply bulkhead BH. The "
                        "U formers are open at the top so the bottle lifts out.",
                  items=items, traps=[]))

    # ---------------------------------------------------------------- keels, longerons
    items = [P("Keel-R"), P("Keel-L"), P("Longeron-R1"), P("Longeron-R2"), P("Longeron-L1"), P("Longeron-L2"),
             A("strips-ca", "Wick thin CA where the keels and longerons cross the formers",
               needs=[(n, "order", "Fit all six strips before gluing.") for n in
                      ["Keel-R", "Keel-L", "Longeron-R1", "Longeron-R2", "Longeron-L1", "Longeron-L2"]])]
    S.append(dict(id="strips", phase="Pod", title="Keels and longerons", view="pod-iso", mode="slot",
                  intro="Two 3 x 5 mm keels run along the floor through notches in the formers (FS to BH). The 6 x 6 mm "
                        "L-section longerons (two 1.5 mm strips, 6 and 4.5 wide, glued in the corner) sit in the floor/side corners, in two pieces per side (gaps at the release "
                        "servo and the grip). Strip stock, cut to the lengths in the BOM.",
                  items=items,
                  traps=[T("keel-sides-first", "Leave the longerons out until the sides are on",
                           "The longerons sit inside the floor/side corner: once the sides are glued there is no room to "
                           "push them in and press them home.", "Fit the longerons now, before the sides.", "order")]))

    # ---------------------------------------------------------------- sides
    lam = [("LAM-RN", "Right nose panel", ["RO-NL", "RO-NU", "RI-N1", "RI-N2"]),
           ("LAM-RM", "Right middle panel", ["RO-M1L", "RO-M1U", "RO-MP", "RO-M3L", "RO-M3U", "RI-M1", "RI-M2U", "RI-M2G",
                                             "RI-M3U", "RI-M3G", "RI-M4", "RI-M5", "SD-R"]),
           ("LAM-RT", "Right tail-cone panel", ["RO-TL", "RO-TU", "RI-T1"]),
           ("LAM-LN", "Left nose panel", ["LO-NL", "LO-NU", "LI-N1", "LI-N2"]),
           ("LAM-LM", "Left middle panel", ["LO-ML", "LO-MU", "LI-M1", "LI-M2U", "LI-M2G", "LI-M3U", "LI-M4", "LI-M5", "SD-L"]),
           ("LAM-LT", "Left tail-cone panel", ["LO-TL", "LO-TU", "LI-T1"])]
    items = [A("pins-J2", "Push 2 x PIN-6x11 into each of the four J2 hole pairs (JB-B)"),
             P("J2-1R-SQUARE", needs=[("pins-J2", "pin", "The J2 squares drop onto pins in JB-B. Pins first.")]),
             P("J2-1L-SQUARE", needs=[("pins-J2", "pin", "The J2 squares drop onto pins in JB-B. Pins first.")]),
             P("J2-2R-SQUARE", needs=[("pins-J2", "pin", "The J2 squares drop onto pins in JB-B. Pins first.")]),
             P("J2-2L-SQUARE", needs=[("pins-J2", "pin", "The J2 squares drop onto pins in JB-B. Pins first.")]),
             A("pins-J3", "Push 2 x PIN-6x11 into each J3 hole pair (JB-A)"),
             P("J3-R-NOSE-TAPER", needs=[("pins-J3", "pin", "J3 sits on two pins in JB-A. Pins first.")]),
             P("J3-L-NOSE-TAPER", needs=[("pins-J3", "pin", "J3 sits on two pins in JB-A. Pins first.")])]
    for gid, label, mem in lam:
        side = gid[4]
        seg = gid[5]
        needs = []
        if seg == "N":
            needs.append(("J3-%s-NOSE-TAPER" % side, "jig", "The nose panel is held at its plan angle by J3-%s. Pin J3 first." % side))
        if seg == "M":
            needs += [("J2-1%s-SQUARE" % side, "jig", "The middle panel is held vertical by the J2 squares while the joints cure. Pin J2 first."),
                      ("J2-2%s-SQUARE" % side, "jig", "The middle panel is held vertical by the J2 squares while the joints cure. Pin J2 first.")]
        if gid == "LAM-LM":
            needs.append(("TST", "order", "The tail-servo tray's tabs go through both middle panels: fit TST into the right "
                                          "panel before the left panel closes the gap."))
        items.append(K(gid, "%s (%s)" % (label, ", ".join(mem)), mem, needs=needs))
        if gid == "LAM-RM":
            items.append(P("TST", needs=[("LAM-RM", "order", "TST's right tabs go into the slots in the right middle panel: put that panel on first.")],
                           why="Tail-servo tray, 2 x 1.5 mm balsa laminated (grain crossed)."))
    items.append(A("sides-ca", "Wick thin CA into the finger joints and along every former tab, J2 and J3 still in place",
                   needs=[(g, "order", "All six panels must be on their tabs before gluing.") for g, _, _ in lam]))
    S.append(dict(id="sides", phase="Pod", title="Sides onto the tabs, J2 and J3 in place", view="pod-top", mode="slot",
                  intro="Each laminated panel drops over the former side tabs; the finger tabs on its bottom edge drop into "
                        "the notches in the floor edge. The panels carry the names of the formers whose tabs go through "
                        "them. Engraved faces IN. J2 squares hold the middle panels vertical, J3 blocks hold the nose "
                        "panels at their taper.",
                  items=items,
                  traps=[T("sides-clamp", "Clamp the panels hard against the formers with spring clamps",
                           "Clamps crush 2.5 mm balsa laminate and pull the panels out of line. The tabs and jigs already "
                           "position everything.", "Let the jigs hold the panels; tape lightly if a panel springs out.")]))

    # ---------------------------------------------------------------- nose ring, firewall, hard points
    items = [A("epoxy-mix-1", "Mix a little 5-minute epoxy"),
             P("NOSE-RING", needs=[("LAM-RN", "order", "The nose ring's glue sleeve goes inside both nose panels: sides first."),
                                   ("LAM-LN", "order", "The nose ring's glue sleeve goes inside both nose panels: sides first."),
                                   ("epoxy-mix-1", "glue", "The PETG ring is glued with epoxy (CA does not hold PETG well).")],
               why="Printed PETG: front lip, collar for the firewall, glue sleeve inside the panels."),
             P("FW", needs=[("NOSE-RING", "order", "The firewall sits in the nose-ring collar against the lip: the motor pulls it "
                                                    "forward onto the lip. Ring first.")], why="Firewall, 2 x 1.5 mm birch ply laminated (face grain crossed), 'UP ^' up."),
             P("SERVO-MOUNT", needs=[("LAM-RM", "order", "The release-servo mount fits through the window in the right ply insert RO-MP: right middle panel first.")],
               why="Printed PETG arm pocket and servo shelves (D-059)."),
             P("STUB-R", needs=[("LAM-RM", "order", "The band stub goes through the right side and its doubler SD-R.")],
               why="Carbon rod, front rubber-band stub."),
             P("STUB-L", needs=[("LAM-LM", "order", "The band stub goes through the left side and its doubler SD-L.")],
               why="Carbon rod, front rubber-band stub."),
             P("DOWEL", needs=[("LAM-RT", "order", "The rear band dowel passes through both tail-cone panels."),
                               ("LAM-LT", "order", "The rear band dowel passes through both tail-cone panels.")],
               why="Birch dowel, rear rubber-band anchor.")]
    S.append(dict(id="nose", phase="Pod", title="Nose ring, firewall and hard points", view="pod-iso", mode="slot",
                  intro="The printed nose ring takes the motor load into the nose panels; the laminated birch firewall sits in its "
                        "collar. The release-servo mount, the band stubs and the rear dowel are the other hard points.",
                  items=items,
                  traps=[T("fw-ca", "Glue the nose ring with thin CA only",
                           "Thin CA on PETG makes a weak, brittle joint that can let go under motor vibration.",
                           "Scuff the PETG with 150 grit and use epoxy.")]))

    # ---------------------------------------------------------------- booms
    items = [A("pins-J4", "Push 2 x PIN-6x11 into each J4 hole pair (JB-C and JB-D2)"),
             P("J4a-BOOM-CRADLE", needs=[("pins-J4", "pin", "J4a sits on two pins. Pins first.")]),
             P("J4b-BOOM-CRADLE", needs=[("pins-J4", "pin", "J4b sits on two pins. Pins first.")]),
             P("TR1R"), P("TR1L"), P("TR2R"), P("TR2L"),
             P("BOOM-R", needs=[("J4a-BOOM-CRADLE", "jig", "The booms must lie in both J4 cradles while the glue cures: the cradles set the tail incidence."),
                                ("J4b-BOOM-CRADLE", "jig", "The booms must lie in both J4 cradles while the glue cures: the cradles set the tail incidence."),
                                ("TR1R", "order", "Glue the tube rings to BH and EF first; the boom slides through them."),
                                ("TR2R", "order", "Glue the tube rings to BH and EF first; the boom slides through them.")]),
             P("BOOM-L", needs=[("J4a-BOOM-CRADLE", "jig", "The booms must lie in both J4 cradles while the glue cures: the cradles set the tail incidence."),
                                ("J4b-BOOM-CRADLE", "jig", "The booms must lie in both J4 cradles while the glue cures: the cradles set the tail incidence."),
                                ("TR1L", "order", "Glue the tube rings to BH and EF first; the boom slides through them."),
                                ("TR2L", "order", "Glue the tube rings to BH and EF first; the boom slides through them.")]),
             A("booms-check", "Check: J4a's front face flat on EF, both booms down in both cradles",
               needs=[("BOOM-R", "order", "Both booms in first."), ("BOOM-L", "order", "Both booms in first.")]),
             A("booms-epoxy", "Slow epoxy (Araldite Standard) the booms into BH, EF and the tube rings; leave the cradles pinned overnight",
               needs=[("booms-check", "order", "Check the booms are seated before the glue goes on.")])]
    for it in items:
        if it["id"] in ("TR1R", "TR1L"):
            it["needs"] = [("BH", "order", "Tube ring on the bulkhead's aft face.")]
        if it["id"] in ("TR2R", "TR2L"):
            it["needs"] = [("EF", "order", "Tube ring on the end former's front face.")]
    S.append(dict(id="booms", phase="Pod", title="Booms through the bulkhead on the J4 cradles", view="pod-iso", mode="slot",
                  intro="Two 10/8 mm carbon tubes pass through the bulkhead BH and end former EF, with birch tube rings (2 x 1.5 mm) "
                        "on BH's aft face and EF's front face. The J4 cradles hold them parallel at Y +-16, Z -40. This "
                        "is the step that sets the tail incidence.",
                  items=items,
                  traps=[T("booms-lift", "Lift the booms out of the cradles while the epoxy cures so it runs into the joint",
                           "Off the cradles the booms are not parallel to the pod datum: the tail incidence is set wrong "
                           "and cannot be fixed later.", "Keep the booms down in both J4 cradles until the epoxy is hard.", "jig")]))

    # ---------------------------------------------------------------- deck, capstrip, ledges, hatch, J5
    items = [P("DECK", needs=[("BH", "order", "BH's top tabs come up through the deck."), ("EF", "order", "EF's top tabs come up through the deck."),
                              ("LAM-RT", "order", "The deck sits inside the tail-cone sides."), ("LAM-LT", "order", "The deck sits inside the tail-cone sides.")]),
             P("Capstrip-R", needs=[("LAM-RM", "order", "The capstrip is glued along the inside top of the side panel.")]),
             P("Capstrip-L", needs=[("LAM-LM", "order", "The capstrip is glued along the inside top of the side panel.")]),
             P("Ledge-R1", needs=[("LAM-RN", "order", "The hatch ledge is glued inside the nose panel.")]),
             P("Ledge-L1", needs=[("LAM-LN", "order", "The hatch ledge is glued inside the nose panel.")]),
             P("Ledge-R2", needs=[("LAM-RM", "order", "The front hatch ledge is glued inside the middle panel.")]),
             P("Ledge-L2", needs=[("LAM-LM", "order", "The front hatch ledge is glued inside the middle panel.")]),
             P("HN-R", slot=False), P("HN-L", needs=[("HN-R", "order", "The hatch halves key together with dovetails: one half down first.")], slot=False),
             P("HF", slot=False),
             P("J5a-SEAT-GAUGE", needs=[("Capstrip-R", "order", "J5 checks the capstrip and side tops: glue the capstrips first."),
                                        ("Capstrip-L", "order", "J5 checks the capstrip and side tops: glue the capstrips first.")]),
             P("J5b-SEAT-GAUGE", needs=[("Capstrip-R", "order", "Glue the capstrips first."), ("Capstrip-L", "order", "Glue the capstrips first.")]),
             A("sand-J5", "Sand the side tops and capstrips with a long block until J5a and J5b sit without rocking",
               needs=[("J5a-SEAT-GAUGE", "jig", "Sanding the wing seat by eye gives the wrong incidence: sand against J5a/J5b."),
                      ("J5b-SEAT-GAUGE", "jig", "Sand against J5b too: it covers X 140 to 280.")])]
    S.append(dict(id="deck", phase="Pod", title="Aft deck, capstrip, hatch; sand the wing seat with J5", view="pod-iso", mode="slot",
                  intro="The 1.5 mm aft deck drops over the top tabs of BH and EF. The 6 x 3 mm capstrips are bent along the "
                        "top of the middle panels (the wing seat), the 3 x 3 mm ledges carry the hatch. The hatch "
                        "(HN-R + HN-L keyed together, HF) stays REMOVABLE. J5a/J5b are the wing's lower surface at +3 deg "
                        "plus 1 mm foam: sand until they do not rock.",
                  items=items,
                  traps=[T("hatch-glue", "Glue the hatch onto the ledges",
                           "The hatch is the only way to the battery and the bottle's fill cap.",
                           "Glue HN-R to HN-L (and HF) only; the hatch is held by the 4 magnet pairs.")]))

    # ---------------------------------------------------------------- saddles
    items = [P("PAD-S1", why="Birch bearing pad under saddle S1: spreads the landing load over the skid (floor crushing, P2)."),
             P("PAD-S2", why="Birch bearing pad under saddle S2."),
             A("cling", "Wrap the bottle in cling film"),
             P("S1a", needs=[("cling", "order", "Wrap the bottle first, or the saddle layers glue themselves to the bottle.")], slot=False),
             P("S1b", needs=[("S1a", "order", "Stack the layers in order a, b, c, d.")], slot=False),
             P("S1c", needs=[("S1b", "order", "Stack the layers in order a, b, c, d.")], slot=False),
             P("S1d", needs=[("S1c", "order", "Stack the layers in order a, b, c, d.")], slot=False),
             P("S2a", needs=[("cling", "order", "Wrap the bottle first.")], slot=False),
             P("S2b", needs=[("S2a", "order", "Stack the layers in order a, b, c, d.")], slot=False),
             P("S2c", needs=[("S2b", "order", "Stack the layers in order a, b, c, d.")], slot=False),
             P("S2d", needs=[("S2c", "order", "Stack the layers in order a, b, c, d.")], slot=False),
             A("toothpicks", "Push three 2 mm toothpicks through the pin holes of each stack and glue the layers together (PVA)",
               needs=[("S1d", "order", "All four layers of S1 first."), ("S2d", "order", "All four layers of S2 first.")]),
             A("saddles-in", "Lower the wrapped bottle with both stacks into the pod: saddle tabs into the floor slots, the notch in each stack over its pad; glue to the floor",
               needs=[("toothpicks", "order", "Pin and glue each stack before it goes in."),
                      ("PAD-S1", "order", "Glue the bearing pads on the floor first: the saddles sit on them."),
                      ("PAD-S2", "order", "Glue the bearing pads on the floor first.")]),
             P("S1BR", needs=[("saddles-in", "order", "The strap bridges go in after the saddles.")], slot=False),
             P("S1BL", needs=[("saddles-in", "order", "The strap bridges go in after the saddles.")], slot=False),
             P("S2BR", needs=[("saddles-in", "order", "The strap bridges go in after the saddles.")], slot=False),
             P("S2BL", needs=[("saddles-in", "order", "The strap bridges go in after the saddles.")], slot=False),
             A("bottle-out", "When the glue is hard, lift the bottle out and peel off the cling film",
               needs=[("saddles-in", "cure", "Let the saddles cure on the bottle first.")])]
    S.append(dict(id="saddles", phase="Pod", title="Saddle stacks on the bottle", view="pod-iso", mode="place",
                  intro="Each saddle is 4 layers (a to d, each 2 x 1.5 mm balsa laminated with crossed grain), with "
                        "lightening windows, keel notches and 3 pin holes. Building them on the real bottle gives a perfect "
                        "fit. Strap bridges S1BR/S1BL/S2BR/S2BL drop their legs through floor slots.",
                  items=items,
                  traps=[T("saddle-bare", "Glue the stack directly onto the bare bottle",
                           "PVA and CA stick to the PET bottle: the bottle will not come out for filling, cleaning or the release.",
                           "Wrap the bottle in cling film first.")]))

    # ---------------------------------------------------------------- wing cradles
    wc = []
    for k in range(1, 6):
        for s in "RL":
            wc.append(P("WC%d%s-F" % (k, s), needs=[("le-line", "order", "Draw the LE line first: every front half's LE stop sits on it.")]))
            wc.append(P("WC%d%s-R" % (k, s), needs=[("WC%d%s-F" % (k, s), "order", "The rear half keys onto its front half with a dovetail: front half first.")]))
    items = [A("le-line", "Draw one straight line on the 1 m wing board for the leading edge")] + wc + \
            [A("wc-screws", "Screw every cradle half to the board: 2 x 4 mm wood screws each",
               needs=[(it["id"], "order", "Place all 20 halves first, check them against the line, then screw.") for it in wc])]
    S.append(dict(id="wing-cradles", phase="Wing", title="Wing cradles on the board", view="wing-top", mode="slot",
                  intro="Ten cradles (WC1 to WC5, right and left), each a front half ('< LE') and a rear half ('TE >') "
                        "keyed with a dovetail. Their top faces are the airfoil lower surface: they set the airfoil and "
                        "zero twist. The LE stops all sit on one straight line.",
                  items=items,
                  traps=[T("wc-eye", "Line the cradles up by eye", "A few mm of error at one cradle twists the wing.",
                           "Use the straight LE line and a steel rule; measure each station from the centre (27.5, 137.5, 247.5, 357.5, 465 mm).")]))

    # ---------------------------------------------------------------- wing bottom
    items = [P("DBOX-BOT", why="1.5 mm balsa (use the lightest sheets), the lower D-box skin."),
             P("CAP-C-BOT", needs=[("DBOX-BOT", "order", "Lay the bottom D-box sheet first; the spar cap sits on it at X 72.6-78.6.")],
               why="0.5 x 6 mm carbon (two 3 x 0.5 strips side by side): the outer face of the bottom spar cap."),
             P("CAP-B-BOT", needs=[("CAP-C-BOT", "order", "The carbon is the OUTER face of the bottom cap: carbon first, the balsa cap on top of it.")],
               why="3 x 6 mm balsa: two 1.5 x 6 strips laminated."),
             P("CS-BF-R"), P("CS-BF-L"), P("CS-BA-R"), P("CS-BA-L"),
             A("epoxy-caps", "Slow epoxy between the carbon and the balsa cap; pin or tape the sheeting into the cradles",
               needs=[("CAP-B-BOT", "order", "Both cap layers in first.")])]
    S.append(dict(id="wing-bottom", phase="Wing", title="Bottom sheeting and spar cap", view="wing-iso", mode="slot",
                  intro="The wing is built upside-up, lower surface down in the cradles. First the lower D-box sheet, the "
                        "bottom spar cap (carbon outside, balsa inside) and the four bottom centre-sheeting panels "
                        "(grain chord-wise).",
                  items=items, traps=[]))

    # ---------------------------------------------------------------- ribs
    items = [P(n) for n in RIBS] + [P("W-TIPCAP-R", needs=[("W-TIP-R", "order", "The tip cap goes on the outside of the tip rib.")]),
                                    P("W-TIPCAP-L", needs=[("W-TIP-L", "order", "The tip cap goes on the outside of the tip rib.")])]
    for it in items[:len(RIBS)]:
        it["needs"] = [("CAP-B-BOT", "order", "The ribs' notches drop over the bottom spar cap: cap first.")]
    S.append(dict(id="wing-ribs", phase="Wing", title="Ribs onto the spar cap", view="wing-top", mode="slot",
                  intro="19 one-piece ribs from the LE stock to the TE stock (aileron-span ribs stop at the false spar). Each "
                        "rib's notch drops over the bottom cap; '< LE' to the front. The ribs are 1.5 mm; W-C and W-R110 are 2 x 1.5 mm laminated (wing bolt-down "
                        "and servo bay), the tip ribs are one 1.5 mm layer.",
                  items=items, traps=[]))

    # ---------------------------------------------------------------- false spar, webs, servo frames
    items = [P("FSP-C"), P("FSP-R1", needs=[("FSP-C", "order", "FSP-R1 keys into FSP-C with a dovetail: centre piece first.")]),
             P("FSP-L1", needs=[("FSP-C", "order", "FSP-L1 keys into FSP-C with a dovetail: centre piece first.")]),
             P("FSP-R2", needs=[("FSP-R1", "order", "FSP-R2 keys into FSP-R1.")]),
             P("FSP-L2", needs=[("FSP-L1", "order", "FSP-L2 keys into FSP-L1.")])]
    items += [P(n) for n in WEBS]
    items += [P("SERVO-FRAME-R", why="Printed PETG frame of the right aileron-servo bay."),
              P("SERVO-FRAME-L", why="Printed PETG frame of the left aileron-servo bay."),
              A("webs-glue", "PVA on the web faces against the caps; thin CA on the egg-crate joints",
                needs=[(n, "order", "All webs in first.") for n in WEBS])]
    S.append(dict(id="wing-spar", phase="Wing", title="Egg-crate false spar and shear webs", view="wing-top", mode="slot",
                  intro="The 3 mm false spar (2 x 1.5 mm laminated, grain span-wise) is 5 pieces keyed with dovetails; it is slotted from below "
                        "and the ribs from above, so they lock together (egg-crate). The CA-hinge slots in it are laser cut. "
                        "The 1.5 mm shear webs (grain vertical) sit between the ribs in front of (WF) and behind (WR) the "
                        "spar caps; their end tabs lock into the rib slots.",
                  items=items, traps=[]))

    # ---------------------------------------------------------------- top
    capR, capL = caps("R", "T", names), caps("L", "T", names)
    items = [P("CAP-B-TOP", needs=[("webs-glue", "order", "The webs must be in before the top cap closes the spar box.")]),
             P("CAP-C-TOP", needs=[("CAP-B-TOP", "order", "The carbon is the OUTER (top) face: balsa cap first, carbon on top.")]),
             P("LE"), P("TE-C"), P("TE-O-R"), P("TE-O-L"),
             P("DBOX-TOP", needs=[("CAP-C-TOP", "order", "The top D-box sheet covers the spar cap: cap first."),
                                  ("LE", "order", "The top D-box sheet runs from the LE stock: LE first.")]),
             P("CS-TF-R", needs=[("CAP-C-TOP", "order", "Centre sheeting over the cap: cap first.")]),
             P("CS-TF-L", needs=[("CAP-C-TOP", "order", "Centre sheeting over the cap: cap first.")]),
             P("CS-TA-R"), P("CS-TA-L"),
             K("CAPS-TOP-R", "Right top cap strips (%s)" % ", ".join(capR), capR, orient=False),
             K("CAPS-TOP-L", "Left top cap strips (%s)" % ", ".join(capL), capL, orient=False)]
    for it in items:
        if it["id"] in ("LE", "TE-C", "TE-O-R", "TE-O-L"):
            it["needs"] = [("webs-glue", "order", "Glue the webs and egg-crate joints first, so the frame is square.")]
    S.append(dict(id="wing-top", phase="Wing", title="Top cap, LE, TE and top sheeting", view="wing-iso", mode="slot",
                  intro="Top spar cap (balsa, then carbon), the 6 mm LE (4 x 1.5 mm laminated and shaped), the TE wedges (staggered 1.5 mm strips sanded to the wedge), then the top "
                        "sheeting last: D-box, centre sheeting and the 1.5 x 6 mm cap strips on every rib.",
                  items=items, traps=[]))

    # ---------------------------------------------------------------- off the cradles
    capRB, capLB = caps("R", "B", names), caps("L", "B", names)
    items = [A("wing-off", "Lift the wing straight up out of the cradles (the cradles stay screwed to the board)"),
             K("CAPS-BOT-R", "Right bottom cap strips (%s)" % ", ".join(capRB), capRB, orient=False,
               needs=[("wing-off", "order", "The bottom cap strips go on after the wing comes out of the cradles.")]),
             K("CAPS-BOT-L", "Left bottom cap strips (%s)" % ", ".join(capLB), capLB, orient=False,
               needs=[("wing-off", "order", "The bottom cap strips go on after the wing comes out of the cradles.")]),
             A("sand-le", "Sand the LE stock to the airfoil nose and the sheeting edges flush",
               needs=[("wing-off", "order", "Take the wing off the cradles first.")])]
    S.append(dict(id="wing-off", phase="Wing", title="Off the cradles: bottom cap strips, sand", view="wing-iso", mode="slot",
                  intro="Lift the finished centre structure off the cradles, add the bottom cap strips and sand the LE.",
                  items=items,
                  traps=[T("wing-off-early", "Take the wing off as soon as the top sheeting is down",
                           "Glue that is not cured lets the wing spring into a twist.", "Leave it in the cradles overnight.", "order")]))

    # ---------------------------------------------------------------- ailerons
    items = []
    for s in "RL":
        a = ail(s)
        for n in a:
            needs = []
            if n != "AIL-LE-" + s:
                needs.append(("AIL-LE-" + s, "order", "Build each aileron on its LE strip: AIL-LE-%s first." % s))
            if n == "AIL-TE-" + s:
                needs = [(m, "order", "Every aileron rib goes in before the TE wedge closes the frame.") for m in a if m != n]
            items.append(P(n, needs=needs, slot=False))
        items.append(A("bevel-" + s, "Sand the 25 deg V-bevel on AIL-LE-%s" % s,
                       needs=[("AIL-TE-" + s, "order", "Finish the aileron frame first.")]))
        items.append(A("slits-" + s, "Cut the 4 hinge slits (9 mm deep) in AIL-LE-%s with a hinge-slotting knife" % s,
                       needs=[("bevel-" + s, "order", "Bevel first, then slit: the slits run along the middle of the bevelled strip.")]))
        hg = ["HINGE-AIL-%s%d" % (s, k) for k in range(1, 5)]
        items.append(K("HINGES-AIL-" + s, "Dry-fit the %s aileron hinges, NO glue (%s)" % ({"R": "right", "L": "left"}[s], ", ".join(hg)),
                       hg, orient=False, slot=False,
                       needs=[("slits-" + s, "order", "Cut the slits first.")]))
    S.append(dict(id="ailerons", phase="Wing", title="Ailerons, V-bevel, hinge slits (dry fit)", view="wing-iso", mode="place",
                  intro="Each aileron: a 3 mm LE strip, 7 ribs A112 to A437, the 2 mm horn rib AH and the TE wedge. Sand "
                        "the 25 deg V-bevel so the aileron reaches its throw, cut the hinge slits by hand and dry-fit the "
                        "CA hinges. Hinges are glued AFTER covering.",
                  items=items,
                  traps=[T("hinge-glue-early", "Glue the CA hinges in now",
                           "Glued hinges before covering: you cannot iron the film into the hinge gap and the surface "
                           "cannot come off to be covered.", "Dry-fit now; glue the hinges after covering (step 'Hinges').", "order")]))

    # ---------------------------------------------------------------- tail
    items = [A("epoxy-mix-2", "Mix 5-minute epoxy"),
             P("TAIL-BLOCK", needs=[("BOOM-R", "order", "The tail block's collars slide over the boom ends."),
                                    ("BOOM-L", "order", "The tail block's collars slide over the boom ends."),
                                    ("epoxy-mix-2", "glue", "Epoxy the PETG collars to the carbon tubes.")],
               why="Printed PETG: plate with the fin slots, two collars, two webs."),
             P("FIN", needs=[("TAIL-BLOCK", "order", "The fin's two root tabs go into the slots in the tail-block plate.")]),
             P("TJ2-STAB-LEVEL", needs=[("TAIL-BLOCK", "order", "TJ2 stands on both booms ahead of the fin: block and fin first."),
                                        ("FIN", "order", "TJ2 stands on both booms ahead of the fin.")]),
             P("STAB-R", needs=[("FIN", "order", "The stab tabs pass through the slots in the fin: fin first."),
                                ("TJ2-STAB-LEVEL", "jig", "TJ2 under the stab sets 0 deg stab incidence to the booms. Put it in first.")]),
             P("STAB-L", needs=[("FIN", "order", "The stab tabs pass through the slots in the fin: fin first."),
                                ("TJ2-STAB-LEVEL", "jig", "TJ2 under the stab sets 0 deg stab incidence to the booms. Put it in first.")]),
             P("TJ1-RU-SQUARE", needs=[("STAB-R", "order", "TJ1 squares the fin to the stab half: stab half first.")]),
             P("TJ1-RD-SQUARE", needs=[("STAB-R", "order", "TJ1 squares the fin to the stab half: stab half first.")]),
             P("TJ1-LU-SQUARE", needs=[("STAB-L", "order", "TJ1 squares the fin to the stab half: stab half first.")]),
             P("TJ1-LD-SQUARE", needs=[("STAB-L", "order", "TJ1 squares the fin to the stab half: stab half first.")]),
             A("tail-ca", "Thin CA on the stab tabs and the fin root, with TJ1 x 4 and TJ2 in place",
               needs=[("TJ1-RU-SQUARE", "jig", "All four TJ1 squares must be in the corners when the glue goes on."),
                      ("TJ1-RD-SQUARE", "jig", "All four TJ1 squares must be in the corners when the glue goes on."),
                      ("TJ1-LU-SQUARE", "jig", "All four TJ1 squares must be in the corners when the glue goes on."),
                      ("TJ1-LD-SQUARE", "jig", "All four TJ1 squares must be in the corners when the glue goes on.")]),
             P("ELEV-R", slot=True), P("ELEV-L", slot=True),
             K("JOINER-WIRE", "Elevator joiner wire (JOINER, JOINER-LEG-R, JOINER-LEG-L)", ["JOINER", "JOINER-LEG-R", "JOINER-LEG-L"],
               orient=False, needs=[("ELEV-R", "order", "The joiner wire lies in slots in both elevator halves."),
                                    ("ELEV-L", "order", "The joiner wire lies in slots in both elevator halves.")]),
             P("RUDDER"),
             P("HORN-E", needs=[("ELEV-L", "order", "The elevator horn goes under the LEFT elevator half.")], orient=False),
             P("HORN-R", needs=[("RUDDER", "order", "The rudder horn goes on the right of the rudder.")], orient=False),
             A("tail-bevel", "Sand the 25 deg V-bevel on the elevator and rudder LEs; cut the hinge slits (6.5 mm in the fixed part, 4.5 mm in the moving part)",
               needs=[("JOINER-WIRE", "order", "Elevator halves joined first."), ("RUDDER", "order", "Rudder first.")]),
             K("HINGES-TAIL", "Dry-fit the tail hinges, NO glue (HINGE-ELEV-R1..3, HINGE-ELEV-L1..3, HINGE-RUD-1..3)",
               ["HINGE-ELEV-R1", "HINGE-ELEV-R2", "HINGE-ELEV-R3", "HINGE-ELEV-L1", "HINGE-ELEV-L2", "HINGE-ELEV-L3",
                "HINGE-RUD-1", "HINGE-RUD-2", "HINGE-RUD-3"], orient=False, slot=False,
               needs=[("tail-bevel", "order", "Cut the hinge slits first.")])]
    for n in ("ELEV-R", "ELEV-L", "RUDDER"):
        for it in items:
            if it["id"] == n:
                it["needs"] = [("tail-ca", "cure", "Glue the fixed tail (fin and stab) first; the moving surfaces are fitted to it.")]
    S.append(dict(id="tail", phase="Tail", title="Tail: fin, stabiliser with TJ1 / TJ2, elevator, rudder", view="tail-iso", mode="slot",
                  intro="The printed tail block sits on the boom ends; the fin's root tabs go into its plate. The two "
                        "stabiliser halves pass their tabs through the 4 slots in the fin (right and left tabs alternate). "
                        "TJ2 on the booms keeps the stab level with the booms, the four TJ1 squares keep the fin at 90 deg.",
                  items=items,
                  traps=[T("tail-by-eye", "Glue the stab by eye and check it later from behind",
                           "A stab that is not level with the booms gives a rolling tendency and pitch trim you cannot remove.",
                           "Use TJ2 under the stab and TJ1 in all four corners while the CA cures.", "jig")]))

    # ---------------------------------------------------------------- covering
    items = [A("cover-wing", "Cover the wing: bottom first, then top, film wrapped round the LE; iron at low heat, shrink with the heat gun"),
             A("cover-ail", "Cover the ailerons separately (off the wing)"),
             A("cover-tail", "Cover the stab, elevator, fin and rudder (both sides)"),
             A("cover-pod", "Cover the pod's outer skin (30 g/m2 film); leave the hatch opening and the outlet free"),
             A("cut-slits", "Slice the film open over every hinge slit with a sharp blade",
               needs=[("cover-wing", "order", "Cover first, then open the slits."), ("cover-ail", "order", "Cover the ailerons first."),
                      ("cover-tail", "order", "Cover the tail first.")]),
             P("SK1", needs=[("cover-pod", "order", "The skids go on over the film.")]),
             P("SK2", needs=[("cover-pod", "order", "The skids go on over the film.")]),
             P("SK3", needs=[("cover-pod", "order", "The skids go on over the film.")])]
    S.append(dict(id="cover", phase="Finish", title="Covering and skids", view="pod-iso", mode="slot",
                  intro="Iron-on film: about 0.6 m2 for the wing, 0.17 m2 for the pod and 0.16 m2 for the tail (from the "
                        "mass-table film masses). Light colours stay cooler in the sun. The 1.5 mm ply skids SK1-SK3 go "
                        "under the floor last.",
                  items=items,
                  traps=[T("film-over-slits", "Iron the film over the hinge slits and leave it",
                           "Film over the slit stops the hinge going in, or it tears and lets CA run into the gap.",
                           "Cut the film open over each slit after covering.")]))

    # ---------------------------------------------------------------- hinges
    items = [A("vaseline", "Put a tiny smear of petroleum jelly on the hinge pivot line of each hinge"),
             K("HINGE-SET-AIL-R", "Right aileron hinges (HINGE-AIL-R1..R4)", ["HINGE-AIL-R1", "HINGE-AIL-R2", "HINGE-AIL-R3", "HINGE-AIL-R4"],
               orient=False, slot=False, needs=[("cover-ail", "order", "Hinges go in after covering.")]),
             K("HINGE-SET-AIL-L", "Left aileron hinges (HINGE-AIL-L1..L4)", ["HINGE-AIL-L1", "HINGE-AIL-L2", "HINGE-AIL-L3", "HINGE-AIL-L4"],
               orient=False, slot=False, needs=[("cover-ail", "order", "Hinges go in after covering.")]),
             K("HINGE-SET-ELEV", "Elevator hinges (HINGE-ELEV-R1..R3, L1..L3)",
               ["HINGE-ELEV-R1", "HINGE-ELEV-R2", "HINGE-ELEV-R3", "HINGE-ELEV-L1", "HINGE-ELEV-L2", "HINGE-ELEV-L3"],
               orient=False, slot=False, needs=[("cover-tail", "order", "Hinges go in after covering.")]),
             K("HINGE-SET-RUD", "Rudder hinges (HINGE-RUD-1..3)", ["HINGE-RUD-1", "HINGE-RUD-2", "HINGE-RUD-3"],
               orient=False, slot=False, needs=[("cover-tail", "order", "Hinges go in after covering.")]),
             A("gap-check", "Check a 0.5 mm hinge gap and full throw both ways on every surface",
               needs=[(g, "order", "All hinges in first.") for g in ("HINGE-SET-AIL-R", "HINGE-SET-AIL-L", "HINGE-SET-ELEV", "HINGE-SET-RUD")]),
             A("hinge-ca", "Deflect each surface fully, put 2-3 drops of thin CA on each hinge face (top and bottom); let it wick into the slit",
               needs=[("gap-check", "order", "Check the gap and throw before gluing."),
                      ("vaseline", "glue-gap", "Without the petroleum jelly the CA can wick round the pivot and lock the hinge.")])]
    S.append(dict(id="hinges", phase="Finish", title="Hinges: CA after covering", view="wing-iso", mode="place",
                  intro="CA hinges (0.5 mm hinge sheet, 20 mm wide) in 0.8 mm slits: 4 per aileron, 3 per elevator half, 3 "
                        "in the rudder. Glue each hinge with thin CA from both faces, surface deflected, never along the gap.",
                  items=items,
                  traps=[T("ca-gap", "Run a bead of CA along the hinge gap", "CA in the gap glues the surface solid: the "
                           "hinge cannot bend and the film round it tears.", "Drops on the hinge faces only, surface deflected, so "
                           "the CA wicks into the slit, not the gap.", "glue-gap"),
                         T("hinge-cure-flat", "Glue the hinges with the surfaces at neutral and full of CA",
                           "Flooding the hinge at neutral glues the pivot line itself.",
                           "Deflect the surface while the CA wicks; a few drops per hinge face is enough.", "glue-gap")]))

    # ---------------------------------------------------------------- linkages
    items = [A("servo-tester", "Plug every servo into the receiver (or a servo tester) and centre it: 1500 us, no trims"),
             P("SERVO-W-R", why="MG90S in the right wing bay, shaft outboard."), P("SERVO-W-L", why="MG90S in the left wing bay."),
             P("SERVO-ARM-W-R", needs=[("servo-tester", "neutral", "Fit the arm only with the servo centred, or the arm is off-centre and the throws are unequal."),
                                       ("SERVO-W-R", "order", "Servo in the bay first.")], orient=False),
             P("SERVO-ARM-W-L", needs=[("servo-tester", "neutral", "Fit the arm only with the servo centred."),
                                       ("SERVO-W-L", "order", "Servo in the bay first.")], orient=False),
             P("AIL-HORN-R", needs=[("hinge-ca", "order", "Glue the horn to AH-R and the aileron LE once the hinges are set.")], orient=False),
             P("AIL-HORN-L", needs=[("hinge-ca", "order", "Glue the horn to AH-L and the aileron LE once the hinges are set.")], orient=False),
             N("neutral-AIL-R", "Right aileron: servo at 1500 us, aileron at 0 deg", "Right aileron",
               needs=[("SERVO-ARM-W-R", "order", "Arm first."), ("AIL-HORN-R", "order", "Horn first.")]),
             K("ROD-AIL-R", "Right aileron pushrod with both Z-bends (PUSHROD-AIL-R, ZBEND-AIL-SERVO-R, ZBEND-AIL-HORN-R)",
               ["PUSHROD-AIL-R", "ZBEND-AIL-SERVO-R", "ZBEND-AIL-HORN-R"], orient=False,
               needs=[("neutral-AIL-R", "neutral", "Mark and bend the second Z-bend only with the servo centred and the aileron at 0 deg.")]),
             N("neutral-AIL-L", "Left aileron: servo at 1500 us, aileron at 0 deg", "Left aileron",
               needs=[("SERVO-ARM-W-L", "order", "Arm first."), ("AIL-HORN-L", "order", "Horn first.")]),
             K("ROD-AIL-L", "Left aileron pushrod with both Z-bends (PUSHROD-AIL-L, ZBEND-AIL-SERVO-L, ZBEND-AIL-HORN-L)",
               ["PUSHROD-AIL-L", "ZBEND-AIL-SERVO-L", "ZBEND-AIL-HORN-L"], orient=False,
               needs=[("neutral-AIL-L", "neutral", "Mark and bend the second Z-bend only with the servo centred and the aileron at 0 deg.")]),
             P("SERVO-HATCH-R", needs=[("ROD-AIL-R", "order", "The arm passes through the hatch slot: linkage first.")], orient=False),
             P("SERVO-HATCH-L", needs=[("ROD-AIL-L", "order", "The arm passes through the hatch slot: linkage first.")], orient=False),
             K("TSERVO-RUD", "Rudder servo, MG90S on the tail-servo tray, right (TSERVO-R)", ["TSERVO-R", "TSERVO-TAB1-R", "TSERVO-TAB2-R"],
               orient=False, needs=[("TST", "order", "The servo sits in the tail-servo tray opening.")]),
             K("TSERVO-ELEV", "Elevator servo, MG90S on the tail-servo tray, left (TSERVO-L)", ["TSERVO-L", "TSERVO-TAB1-L", "TSERVO-TAB2-L"],
               orient=False, needs=[("TST", "order", "The servo sits in the tail-servo tray opening.")]),
             P("SERVO-ARM-RUD", needs=[("servo-tester", "neutral", "Centre the servo before fitting the arm."), ("TSERVO-RUD", "order", "Servo first.")], orient=False),
             P("SERVO-ARM-ELEV", needs=[("servo-tester", "neutral", "Centre the servo before fitting the arm."), ("TSERVO-ELEV", "order", "Servo first.")], orient=False),
             N("neutral-ELEV", "Elevator: servo at 1500 us, elevator at 0 deg (level with the stab)", "Elevator",
               needs=[("SERVO-ARM-ELEV", "order", "Arm first."), ("HORN-E", "order", "Horn first.")]),
             K("ROD-ELEV", "Elevator pushrod: 2 mm carbon with steel Z-bend ends (PUSHROD-ELEV, ROD-END-ELEV-SERVO, ROD-END-ELEV-HORN, ZBEND-ELEV-SERVO, ZBEND-ELEV-HORN)",
               ["PUSHROD-ELEV", "ROD-END-ELEV-SERVO", "ROD-END-ELEV-HORN", "ZBEND-ELEV-SERVO", "ZBEND-ELEV-HORN"], orient=False,
               needs=[("neutral-ELEV", "neutral", "Set the elevator to 0 deg and the servo to 1500 us before you fix the rod length.")]),
             N("neutral-RUD", "Rudder: servo at 1500 us, rudder in line with the fin", "Rudder",
               needs=[("SERVO-ARM-RUD", "order", "Arm first."), ("HORN-R", "order", "Horn first.")]),
             K("ROD-RUD", "Rudder pushrod (PUSHROD-RUD, ROD-END-RUD-SERVO, ROD-END-RUD-HORN, ZBEND-RUD-SERVO, ZBEND-RUD-HORN)",
               ["PUSHROD-RUD", "ROD-END-RUD-SERVO", "ROD-END-RUD-HORN", "ZBEND-RUD-SERVO", "ZBEND-RUD-HORN"], orient=False,
               needs=[("neutral-RUD", "neutral", "Set the rudder in line with the fin and the servo to 1500 us before you fix the rod length.")])]
    S.append(dict(id="linkages", phase="Finish", title="Linkages, Z-bends, neutral setting", view="aircraft-iso", mode="place",
                  intro="Ailerons: MG90S in each wing bay, 1.2 mm steel pushrod (70.5 mm between holes) with a Z-bend at each "
                        "end. Tail: two MG90S on the tail-servo tray, 2 mm carbon rods with 1.2 mm steel Z-bend ends, through "
                        "the exit slots in the tail cone. Centre every servo first; make the last Z-bend with the surface at 0 deg.",
                  items=items,
                  traps=[T("trim-fix", "Bend the Z-bend anywhere and centre the surface later with transmitter trim",
                           "Trim uses up servo travel on one side: unequal throws, and the surface is off-centre if the "
                           "model is flown on another transmitter.", "Centre the servo, hold the surface at 0 deg, then mark "
                           "and bend.", "neutral")]))

    # ---------------------------------------------------------------- electronics, CG, checks
    items = [P("MOTOR", needs=[("FW", "order", "The motor bolts to the firewall (4 x M3 on the X-mount circle).")]),
             P("ESC"), P("RECEIVER"), K("REL-SERVO", "Release servo, MG90S on the printed mount (RELEASE-SERVO)", ["RELEASE-SERVO", "RELEASE-SERVO-TAB1", "RELEASE-SERVO-TAB2"],
               orient=False, needs=[("SERVO-MOUNT", "order", "The release servo sits on the printed mount's shelves.")]),
             K("RESERVOIR", "1 L bottle with the outlet, flap and fill unit (BOTTLE, BOTTLE-CAP, OUTLET-PLATE, FLAP, FILL-UNIT)",
               ["BOTTLE", "BOTTLE-CAP", "OUTLET-PLATE", "FLAP", "FILL-UNIT"], orient=False,
               needs=[("bottle-out", "order", "The saddles must be cured and the cling film off."),
                      ("REL-SERVO", "order", "The release servo's link goes to the flap pin: servo first.")]),
             P("BATTERY", needs=[("ESC", "order", "Wire the ESC first.")]),
             A("esc-setup", "PROP OFF: bind the receiver, set the ESC (brake ON), check motor direction and every surface direction",
               needs=[("BATTERY", "order", "Battery in to power up.")]),
             K("PROP", "Prop adapter and 10 x 5 prop (COLLET, PROP-DISC)", ["COLLET", "PROP-DISC"], orient=False,
               needs=[("esc-setup", "safety", "Never fit the prop before the ESC is set up and the motor direction is checked: a "
                                              "motor that starts on the bench is dangerous.")]),
             A("cg", "Balance at X 80 mm behind the wing LE (bottle empty and full): slide the battery on the tray (+-30 mm) to trim",
               needs=[("PROP", "order", "Balance the aircraft complete, prop on."), ("RESERVOIR", "order", "Bottle in.")]),
             A("weigh", "Weigh the empty aircraft and write it in the mass table (score = 996 x 100 / empty mass)",
               needs=[("cg", "order", "Balance first.")]),
             A("release-test", "Fill 1 L, test the release on the bench 3 times; check the safety pin and flag",
               needs=[("cg", "order", "Balance first.")]),
             A("range", "Range check, failsafe (motor off), throws: ailerons about +-15 deg",
               needs=[("release-test", "order", "Release test first.")])]
    S.append(dict(id="final", phase="Finish", title="Electronics, CG and final checks", view="aircraft-iso", mode="place",
                  intro="DYS D2830 motor on the firewall, Skywalker 40A ESC, receiver, 3S 1000 mAh battery on the tray, "
                        "release servo on its mount, the 1 L bottle in the saddles. CG at X 80 (never aft of it: the bottle "
                        "can only move forward).",
                  items=items,
                  traps=[T("prop-first", "Fit the propeller first so you can see the motor direction",
                           "A prop on the bench while you bind and program the ESC can start without warning.",
                           "Check direction with a strip of tape on the bare motor bell; fit the prop last.", "safety"),
                         T("cg-empty-only", "Balance only with the bottle empty",
                           "The water is 62 % of the flight mass: check both states. The water centroid is designed at X 80 so "
                           "the CG does not move at the drop.", "Balance empty and full; both must be at X 80 or slightly ahead.")]))
    return S
