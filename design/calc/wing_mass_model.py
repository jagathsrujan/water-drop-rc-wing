"""Wing mass estimate for four build methods, as a function of chord.
All values are first estimates (interp.) to compare methods; weigh real samples to correct them.
Usage: python3 wing_mass_model.py [chord_m] [t/c]"""
import sys
b = 1.0                 # span, m (rule max)
c = float(sys.argv[1]) if len(sys.argv) > 1 else 0.28
tc = float(sys.argv[2]) if len(sys.argv) > 2 else 0.14   # thickness ratio (SD7062 = 0.14)
S = b * c               # planform area, m^2 (rectangular)
P = 2.05 * c            # airfoil perimeter, m
A_sec = 0.68 * tc * c * c  # airfoil cross-section area, m^2
skin = P * b            # wetted (skin) area, m^2

def spar():  # carbon strip caps 0.5x10 mm + 1.5 mm balsa web, both halves (g)
    return 2 * 0.5e-3 * 10e-3 * b * 1550e3 + 1.5e-3 * 0.8 * tc * c * b * 130e3

m = {}
# Balsa built-up: laser-cut 2 mm ribs at 50 mm, 1.5 mm D-box to 30 % c, TE stock, cap strips, film
ribs = (b / 0.05 + 1) * A_sec * 0.6 * 2e-3 * 128e3
dbox = 0.65 * c * b * 1.5e-3 * 110e3
te_le_caps = 10.0
film = skin * 50          # light film about 50 g/m2 incl. adhesive
glue = 8.0
m['Balsa built-up + film'] = ribs + dbox + te_le_caps + spar() + film + glue
# LW-PLA print: 0.4 mm skin at 0.50 g/cm3 foamed, internal ribs/geodetic about 35 % of skin, carbon spar tube
lw_skin = skin * 0.4e-3 * 500e3
m['LW-PLA print'] = lw_skin * 1.35 + 15 + 6
# XPS hot-wire core 32 kg/m3, 35 % hollowed, spar, tape/laminate skin 40 g/m2, glue
core = A_sec * b * 32e3 * 0.65
m['XPS hot-wire + tape'] = core + spar() + skin * 40 + 8
# Standard PLA: 0.42 mm skin at 1.24 g/cm3, internal 30 %, spar
m['PLA print'] = skin * 0.42e-3 * 1240e3 * 1.30 + 15 + 6

other = 440.0   # rest of empty aircraft without wing (interp.): fuselage+tail, motor, ESC, battery, 4 servos, Rx, reservoir+release, wiring
water = 996.0
print(f"chord {c:.2f} m, area {S:.3f} m2, skin {skin:.3f} m2  (balsa parts: ribs {ribs:.0f} g, D-box {dbox:.0f} g, spar {spar():.0f} g, film {film:.0f} g)")
for k, v in m.items():
    e = other + v
    print(f"{k:24s} wing {v:5.0f} g   empty {e:4.0f} g   score {water/e*100:5.1f}")
