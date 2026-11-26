% P1 single-stock study - hand strength checks of laminated balsa against today's stock (rev B Fusion model).
% Run:  run('P1_single_stock.m')   (from design/optimisation; MATLAB R2024b). Output saved as P1_single_stock.txt.
%
% DESIGN BASIS (see references.md for every source):
%  * Balsa is GENERIC LOCAL STOCK (user rule 2026-11-26): strength at a lower-medium density rho_d = 0.12 g/cm3,
%    mass at medium 0.14 g/cm3 (mass is in p1_stock.py). Better sheets only add margin.
%  * Balsa reference values: Wood Handbook FPL-GTR-190 (2010) Table 5-5a, balsa at 12 % MC, SG 0.16:
%    MOR 21.6 MPa, MOE 3.40 GPa, compression parallel 14.9 MPa, shear parallel 2.1 MPa   [R1]
%  * Linear scaling with density within a species ("linear analysis is suggested", R1 p. 5-26) -> x (0.12/0.16).
%  * Near-minimum (5th percentile) = mean x (1 - 1.645 CoV), CoV from R1 Table 5-6 (MOR 16, compr. par. 18,
%    compr. perp. 28, shear 14 %). Stiffness at the mean.
%  * Across-grain bending strength = 0.04 x along-grain (lowest Q/P for bending, R1 eq. 5-2 list, p. 5-29).
%  * Compression perpendicular (proportional limit): R1 Table 5-11a hardwoods at 12 %: 21,600 G^2.09 kPa
%    (extrapolated below the species data range: estimate).
%  * E_T/E_L = 0.015 (balsa), 0.047 (eastern cottonwood, lite-ply proxy), 0.050 (yellow birch, birch-ply proxy),
%    R1 Table 5-1.
%  * Lite-ply proxy: eastern cottonwood (Populus deltoides) 12 % MC, R1 Table 5-3a: MOR 59 MPa, MOE 9.4 GPa,
%    compr. par. 33.9, compr. perp. 2.6, shear 6.4 MPa. 3 mm = 3 veneers of 1.0 (estimate: lay-up not specified).
%  * Birch-ply proxy: paper birch (Betula papyrifera) 12 % MC, R1 Table 5-3a: MOR 85 MPa, MOE 11.0 GPa,
%    compr. par. 39.2, compr. perp. 4.1, shear 8.3 MPa. 1.0 / 1.5 mm = 3 veneers, 3 mm = 5 veneers (estimate).
%  * Carbon pultruded strip: Easy Composites TDS CFP v1.0 (2024): tensile 400-500 MPa, compressive 200-320 MPa
%    lengthways (lower bound used)   [R3]
%  * Loads: D-064 limit load set (strength_estimate.m), ultimate = 1.5 x limit; wing D-004 (n = 6 ultimate).
clear; fos = 1.5; g = 9.81;

%% ---------------- materials (design values, MPa) ----------------
rho_d = 0.12; rho_hb = 0.16; k = rho_d/rho_hb;          % density scaling
p5 = @(cov) 1 - 1.645*cov;                               % 5th-percentile factor
B.E   = 3400*k;            B.ET = 0.015*B.E;             % balsa along / across (MPa)
B.f   = 21.6*k*p5(0.16);   B.fT = 0.04*B.f;              % bending strength along / across
B.c   = 14.9*k*p5(0.18);                                 % compression parallel
B.s   = 2.1*k*p5(0.14);                                  % shear parallel
B.cp  = 21.6*(rho_d)^2.09*p5(0.28);                      % compression perpendicular (estimate)
P.E   = 9400;  P.ET = 0.047*P.E;  P.f = 59*p5(0.16);  P.fT = 0.04*P.f;   % poplar veneer (lite-ply)
P.c   = 33.9*p5(0.18); P.cp = 2.6*p5(0.28); P.s = 6.4*p5(0.14);
H.E   = 11000; H.ET = 0.050*H.E;  H.f = 85*p5(0.16);  H.fT = 0.04*H.f;   % birch veneer (birch ply)
H.c   = 39.2*p5(0.18); H.cp = 4.1*p5(0.28); H.s = 8.3*p5(0.14);
C.ft  = 400; C.fc = 200;                                 % carbon strip lower bounds
fprintf('DESIGN VALUES (MPa)  balsa rho %.2f: E %.0f, f_bend %.2f, f_bend_across %.2f, f_c %.2f, f_shear %.2f, f_cperp %.3f\n', ...
        rho_d, B.E, B.f, B.fT, B.c, B.s, B.cp);
fprintf('                     lite-ply veneer: f_bend %.1f, f_c %.1f;  birch veneer: f_bend %.1f, f_c %.1f;  carbon f_c %.0f\n\n', ...
        P.f, P.c, H.f, H.c, C.fc);

%% ---------------- laminates: layers {material, t, angle} (angle 0 = grain along the checked direction) ---------
L.liteply3  = {P,1.0,0; P,1.0,90; P,1.0,0};
L.birch1    = {H,1/3,0; H,1/3,90; H,1/3,0};
L.birch15   = {H,0.5,0; H,0.5,90; H,0.5,0};
L.birch3    = {H,0.6,0; H,0.6,90; H,0.6,0; H,0.6,90; H,0.6,0};
L.b15       = {B,1.5,0};
L.b15x2     = {B,1.5,0; B,1.5,90};
L.b15x3     = {B,1.5,0; B,1.5,90; B,1.5,0};
L.b15x4     = {B,1.5,0; B,1.5,90; B,1.5,90; B,1.5,0};
L.b15_b10   = {B,1.5,0; B,1.0,90};                       % today's side laminate (outer along X, inner vertical)
L.b15_h10   = [{B,1.5,0}; L.birch1];                     % today's grip zone
L.b15_h15   = [{B,1.5,0}; L.birch15];
L.b15x2_h15 = [{B,1.5,0; B,1.5,90}; L.birch15];          % FS hybrid: 2 x 1.5 balsa + 1.5 birch face
L.b2x2      = {B,2.0,0; B,2.0,90};
L.b3        = {B,3.0,0};
names = fieldnames(L);
fprintf('%-12s %6s | %26s | %26s\n', 'laminate', 't mm', 'bending eff. allow (0 / 90)', 'in-plane eff. allow (0 / 90)');
for i = 1:numel(names)
    lam = L.(names{i});
    [b0, t] = bend_allow(lam, 0);  b9 = bend_allow(lam, 90);
    m0 = memb_allow(lam, 0);      m9 = memb_allow(lam, 90);
    fprintf('%-12s %6.2f | %12.2f %12.2f | %12.2f %12.2f\n', names{i}, t, b0, b9, m0, m9);
end
fprintf(['(effective allowable = failure moment or force expressed as a homogeneous stress on the full thickness:\n' ...
         ' compare it with sigma = 6M/(b t^2) or N/(b t) computed for the full thickness)\n\n']);

%% ---------------- loads ----------------
m_res = 0.996 + 0.0387;                                  % water + reservoir dry parts in the pod (kg), strength_estimate.m
W_nose = 10*g*m_res;  W_grip = 20;  W_land = 10*g*m_res;  % D-064 LC2, LC3, LC1 (limit, N)
F_mot = 12; T_mot = 0.3e3;                               % D-064 LC4 motor 12 N + 0.3 N m (limit)
M_tail = 7.5e3;                                          % D-064 LC7 boom moment at the bulkhead, both booms (N mm)

rows = {};
add = @(rows, part, check, lamname, sig, allow) [rows; {part, check, lamname, sig, allow, allow/sig}];

%% 1. Front stop FS (out-of-plane): ring 17 wide between 4 spokes, spoke 10 wide, W/4 at 7.5 mm (strength_estimate.m)
Rm = 33.5; sp = 2*pi*Rm/4; q = fos*W_nose/(2*pi*Rm);
for c = {'liteply3','b15x2','b15x4','birch3','b15x2_h15'}
    lam = L.(c{1}); [~, t] = bend_allow(lam, 0);
    a_weak = min(bend_allow(lam,0), bend_allow(lam,90));     % spokes and ring run in both grain directions
    rows = add(rows, 'FS', 'spoke 10 wide, W/4 at 7.5 mm', c{1}, (fos*W_nose/4*7.5)/(10*t^2/6), a_weak);
    rows = add(rows, 'FS', 'ring 17 wide between spokes', c{1}, (q*sp^2/12)/(17*t^2/6), a_weak);
end

%% 2. Formers B1/B2/B4/N1/N2/EF: frame leg 9 wide (in-plane bending), squeeze shared 50 % (strength_estimate.m)
for c = {'liteply3','b15x2','b15x3','b15x4'}
    lam = L.(c{1}); [~, t] = bend_allow(lam, 0);
    a_leg = memb_allow(lam, 0);                          % leg along the outer-layer grain
    a_bar = memb_allow(lam, 90);                         % floor bar across it
    rows = add(rows, 'B1/B4 U-frame', 'leg 9 wide, cantilever 17 mm', c{1}, (0.5*fos*W_grip*17)/(t*9^2/6), a_leg);
    rows = add(rows, 'B1/B4 U-frame', 'side strip 6 wide, fixed-fixed 29', c{1}, (0.5*fos*W_grip*29/8)/(t*6^2/6), a_bar);
end

%% 3. Side panel, finger squeeze 20 N on a 15 mm patch, panel 67 x 95 (Roark centre point load, strength_estimate.m)
b = 67; rp = 7.5; nu = 0.3;
sig_pt = @(W, t) 3*W/(2*pi*t^2) * ((1+nu)*log(2*b/(pi*rp)) + 1);
for c = {'b15_h10','b15_h15','b15_b10','b15x2','b15x3','b2x2'}
    lam = L.(c{1}); [~, t] = bend_allow(lam, 0);
    a = min(bend_allow(lam,0), bend_allow(lam,90));
    rows = add(rows, 'Side grip zone', 'finger squeeze, both directions', c{1}, sig_pt(fos*W_grip, t), a);
end

%% 4. Bulkhead BH with birch tube rings TR1/TR2: boom couple between BH (X 236) and EF (X 302)
Lc = 302 - 236; F_boom = fos*(M_tail/2)/Lc;              % per boom, ultimate (N)
A_ring = pi*(11^2 - 5^2);                                % ring annulus glued to the plate (OD 22, tube 10)
rows = add(rows, 'BH / EF + TR rings', 'ring bearing on tube (3 mm birch ring)', 'birch3', F_boom/(10*3), H.c*0.6);
rows = add(rows, 'BH / EF + TR rings', 'ring-to-plate glue shear on balsa face', 'b15x4', F_boom/A_ring, B.s);
rows = add(rows, 'BH / EF + TR rings', 'plate in-plane bearing at ring OD', 'b15x4', F_boom/(22*6), memb_allow(L.b15x4,0)*B.c/B.f);
rows = add(rows, 'BH / EF (no ring)', 'plate bearing on tube, balsa 4 x 1.5', 'b15x4', F_boom/(10*6), memb_allow(L.b15x4,0)*B.c/B.f);

%% 5. Firewall FW: M3 X-mount, 4 screws at r 9.5 mm (estimate), thrust + torque in-plane bearing
F_scr = fos*(F_mot/4 + T_mot/(4*9.5));
rows = add(rows, 'FW', 'M3 screw bearing, birch 3 mm', 'birch3', F_scr/(3*3), H.c*0.6);
rows = add(rows, 'FW', 'M3 screw bearing, balsa 2 x 1.5', 'b15x2', F_scr/(3*3), B.c*0.5);
% (screw clamp crushing of balsa across the thickness is not computed: the clamp force of a hand-tightened M3 is not
%  known; with f_cperp ~0.14 MPa even 10 N under a 7 mm washer gives 0.3 MPa -> balsa is not used under screws)
rows = add(rows, 'FW', 'M3 washer clamp 10 N (Dw 7) crush, balsa', 'b15x2', 10/(pi/4*(7^2-3.2^2)), B.cp);

%% 6. Saddles: bottle bearing on the cradle edge (arc 100 x 12), in-plane, half the landing load per saddle
rows = add(rows, 'Saddles S1/S2', 'bottle bearing, lite-ply faces (today)', 'liteply3', fos*0.5*W_land/(100*12), P.c*2/3);
rows = add(rows, 'Saddles S1/S2', 'bottle bearing, balsa 2 x 1.5 X', 'b15x2', fos*0.5*W_land/(100*12), B.c*0.5);
rows = add(rows, 'Floor under saddle', 'crushing over skid, saddle + B4 (15 x 15)', 'b15', fos*0.5*W_land/(15*15), B.cp);

%% 7. Wing (D-004, n = 6 ultimate): carbon cap compression, root web shear
M_root = 8.9e3; h_cap = 29 + 0.5;                        % N mm (D-004); cap centroid distance (estimate from SD7062 at 27 % c)
F_cap = M_root/h_cap;
rows = add(rows, 'Wing spar cap', 'carbon 0.5 x 6 compression, n 6', 'carbon', F_cap/(0.5*6), C.fc);
m_load = 0.721 + 0.996; V_root = 6*m_load*g/2;          % ultimate root shear (no wing-mass relief, conservative)
rows = add(rows, 'Wing shear web', 'root web 1.5 x 29 vertical grain', 'b15', V_root/(1.5*29), B.s);
rows = add(rows, 'Wing shear web', 'root web 2 x 1.5 laminated', 'b15x2', V_root/(3.0*29), B.s);

%% ---------------- report ----------------
fprintf('%-20s %-44s %-11s %9s %9s %7s\n', 'Part', 'Check (ultimate = 1.5 x limit)', 'laminate', 'sigma', 'allow', 'margin');
for i = 1:size(rows,1)
    r = rows(i,:);
    fprintf('%-20s %-44s %-11s %9.2f %9.2f %7.2f %s\n', r{1}, r{2}, r{3}, r{4}, r{5}, r{6}, tern(r{6} >= 1, 'OK', 'LOW'));
end
fprintf('\nLoads (limit): nose-in %.0f N, grip %.0f N/side, landing %.0f N, boom couple %.1f N/boom (ult.), motor %.0f N + %.1f N m, wing root shear %.1f N (ult.)\n', ...
        W_nose, W_grip, W_land, F_boom, F_mot, T_mot/1e3, V_root);

%% ---------------- functions ----------------
function [a, t] = bend_allow(lam, ang)
% effective homogeneous bending allowable of a layered strip for bending about the axis normal to 'ang'
n = size(lam,1); t = sum([lam{:,2}]); z = [0 cumsum([lam{:,2}])];
E = zeros(n,1); f = zeros(n,1);
for i = 1:n
    m = lam{i,1}; along = mod(lam{i,3} - ang, 180) == 0;
    if along, E(i) = m.E; f(i) = m.f; else, E(i) = m.ET; f(i) = m.fT; end
end
zc = 0.5*(z(1:n) + z(2:n+1))'; ti = [lam{:,2}]';
zn = sum(E.*ti.*zc)/sum(E.*ti);
EI = sum(E.*(ti.^3/12 + ti.*(zc - zn).^2));
Mi = f.*EI./(E.*max(abs(z(1:n)' - zn), abs(z(2:n+1)' - zn)));
a = 6*min(Mi)/t^2;
end

function a = memb_allow(lam, ang)
% effective homogeneous in-plane (membrane / in-plane bending) allowable: first layer to reach its strength
n = size(lam,1); t = sum([lam{:,2}]); E = zeros(n,1); f = zeros(n,1);
for i = 1:n
    m = lam{i,1}; along = mod(lam{i,3} - ang, 180) == 0;
    if along, E(i) = m.E; f(i) = m.f; else, E(i) = m.ET; f(i) = m.fT; end
end
EA = sum(E.*[lam{:,2}]');
a = min(f.*EA./(E*t));
end

function s = tern(c, a, b)
if c, s = a; else, s = b; end
end
