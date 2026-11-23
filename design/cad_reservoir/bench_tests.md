# Reservoir rev A — bench-test sheet

Tests that must pass before the reservoir design is final: D-037 (curved bulkhead seal, drainage), D-034 (pin pull, opening), D-043/D-050 (vent in the fill cap), D-049 (fill in place).
Unit under test: Bisleri 1 L bottle with the printed outlet unit (P2 to P10) and the fill unit with the vent in the cap (P11), made from `design/cad_reservoir/stl/`. Record each result in the table at the end and in `design/logs/reservoir_cad_log.md`.

## Equipment
- Kitchen scale, 5 kg, 1 g resolution.
- Spring balance or luggage scale, 0 to 2 kg (0 to 20 N).
- Phone stopwatch and phone inclinometer app.
- 1.2 m of clear tube (aquarium air line or 8 to 10 mm tube), a spare bottle cap drilled for the tube, tape measure.
- Jig: a board with the two printed saddles and 2 straps, so the bottle lies as in the aircraft. Shims (coins or balsa) to set the pitch.
- Paper towel (to find a weep), a tray, a towel or 20 mm foam pad.

## Before each test
1. Weigh the dry unit (bottle, outlet unit, vent, both pins). Record the mass.
2. Wet the flap gasket.
3. Insert the release pin and the safety pin.

## T1a — Static head test of the curved bulkhead (D-037)
Purpose: the outlet seal holds the pressure of a 10 g landing. Head at the outlet at 10 g = 10 × 92 mm = 0.92 m of water (9 kPa).
1. Fill the bottle with water. Fit the drilled cap with the tube on the neck.
2. Set the bottle horizontal in the jig, outlet down. Hold the tube vertical.
3. Fill the tube until the water is 0.95 m above the outlet seat.
4. Put dry paper towel under the outlet and the vent. Wait 10 min.
5. Examine the paper towel, the bulkhead edges and the vent.

**Pass:** no wet mark on the towel and no drop at any joint after 10 min.

## T1b — Drop test with full water (D-037, D-034 test 2)
Purpose: the seal and the latch survive a belly landing with full water.
1. Fill with 1000 mL. Close the original cap. Put the unit in the jig.
2. Dry the outside fully. Put the jig belly down on dry paper towel for 1 min to make sure it is dry.
3. Drop the jig flat, belly down, from 0.5 m onto the 20 mm foam pad. Do this 5 times.
4. After each drop, put the jig on dry paper towel for 1 min.

**Pass:** no wet mark after any drop; the flap stays latched; no crack in a printed part.

## T2 — Drain test (D-037, R16)
Purpose: the water left after the release is less than 10 g at 0 to 3° pitch; the drain takes 15 s or less.
1. Weigh the dry unit (mass M0).
2. Fill with 1000 mL (996 g). Put the unit in the jig.
3. Set the jig pitch with the inclinometer: 0° (bottle axis level). Neck end is aft.
4. Pull the safety pin. Pull the release pin by hand with a quick pull. Start the stopwatch at the same time.
5. Stop the stopwatch when the continuous stream stops. Wait 30 s more.
6. Dry the outside of the unit. Weigh it (mass M1). Residual water = M1 − M0.
7. Do steps 2 to 6 at 0°, 3° and 5° nose-up. Do each angle 2 times.
8. Do one more run at 0° with the vent closed by tape. This shows if the vent is necessary.

**Pass:** residual < 10 g at 0° and at 3°; drain time ≤ 15 s. The 5° result is for information (model: 11.5 g).
Model values (estimated bottle): 2.8 g at 0°, 6.4 g at 3°, 11.5 g at 5°; 11.5 s.

## T3 — Pin pull force (D-034 test 1)
Purpose: the MG90S can pull the pin with margin. Limit 8.8 N (50 % of the servo force at a 10 mm arm).
1. Fill with 1000 mL. Wet the flap gasket. Put the unit in the jig at 0°.
2. Pull the safety pin.
3. Hook the spring balance on the release-pin eye. Pull slowly along the pin axis. Read the highest force before the pin moves.
4. Push the pin back in. Do 5 pulls.
5. Do 5 more pulls with the unit tilted 30° to each side (this adds load to the pin).

**Pass:** each pull ≤ 8.8 N (0.9 kg on the scale). Target ≤ 4.4 N. Calculated: about 2.5 N.
If a pull is more than 8.8 N: use a softer gasket (EVA foam), or reduce the gasket compression with a 0.2 mm shim at the latch.

## T4 — Flap opening (D-034 test 3, D-040)
Purpose: the flap opens fully every time and stays out of the stream.
1. Fill with 1000 mL. Put the unit in the jig at 0°.
2. Pull the safety pin and the release pin. Record the open angle of the flap (target ≥ 150°).
3. Do 10 openings. Do 3 of them with a fan or a hair dryer on the cold setting blowing from the front of the bottle.

**Pass:** 10 of 10 openings; the flap never touches the stream; with the air flow the flap trails aft, flat.

## T5 — Vent in the fill cap (D-043, D-050)
Purpose: the silicone flap in the fill cap lets air in at a low pressure and never lets water out.
1. Before you fit the cap: fill the cap with water to 10 mm, flap side up, and hold it over a paper towel for 1 min: no drop. Then blow very gently through the vent holes from the outside: the flap must lift.
2. Fit the cap. The T1a test (0.95 m head) also tests the flap in the closed direction: no weep. Also turn the full bottle upside down (cap at the bottom) for 1 min: no drop.
3. In the T2 drain test, compare the drain time with the vent open and with the vent closed by tape.

**Pass:** no weep at 0.95 m head; the drain with the vent is faster than without it and meets T2.
If the drain with the vent is not faster, or the flap weeps: use a thinner or softer flap, or change to the bought aquarium check valve on the cap (D-050 fallback).

## T6 — Fill in place (D-049)
Purpose: the reservoir fills in the aircraft fast and with a dry exterior.
1. Put the reservoir in the jig, level. Remove the fill cap.
2. Put the printed funnel in the fill port. Pour 1000 mL from a jug at a steady rate. Start the stopwatch at the first pour.
3. Stop the stopwatch when all the water is in. Record the time.
4. Put the cap on. Wipe the outside with a dry paper towel. Examine the towel.
5. Do it 3 times. Do 1 more run with the jig 5° nose-up.

**Pass:** 1000 mL goes in with no overflow; no wet mark on the outside after the cap is on; time ≤ 60 s (target 30 to 45 s, the organizers' limit is not known yet: Q9).

## Results
| Date | Test | Condition | Result | Pass / fail | By |
|---|---|---|---|---|---|
| | T1a | 0.95 m head, 10 min | | | |
| | T1b | 5 drops, 0.5 m | | | |
| | T2 | 0° (2 runs) | g / s | | |
| | T2 | 3° (2 runs) | g / s | | |
| | T2 | 5° (2 runs) | g / s | | |
| | T2 | 0°, vent taped | g / s | | |
| | T3 | 5 pulls level, 5 tilted | max N | | |
| | T4 | 10 openings (3 with air flow) | angle | | |
| | T5 | flap hold / blow | | | |
| | T6 | 3 fills level, 1 at 5° | s | | |

**Photos for the abstract:** take a photo at each test (the static head tube, the drop, the drain stream, the scale reading).
