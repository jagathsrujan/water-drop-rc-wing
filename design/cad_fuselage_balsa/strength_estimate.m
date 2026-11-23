% Fuselage rev B v2 (balsa pod) - hand strength estimate (plate and beam formulas, Roark style).
% Load set D-064 (limit), ultimate = 1.5 x limit. Material values are (interp.) handbook values for the stated densities.
% Margin = allowable / ultimate stress; >= 1.0 holds at ultimate load. Run: run('strength_estimate.m')
clear; fos = 1.5; nu = 0.3;

% ---- materials: allowable bending stress (MPa) ----
balsa_L  = 12.0;   % medium balsa 0.14 g/cm3, along grain (bending)
balsa_T  = 0.8;    % across grain
balsa_X  = 0.5*balsa_L;  % cross-laminated 2 x 1.5 mm: one layer along grain in each direction (conservative)
liteply  = 25.0;   % poplar lite-ply 0.45
birchply = 40.0;   % birch aircraft ply 0.65
balsa_crush = 0.6; % balsa across the thickness (crushing)

% ---- loads ----
m_water_res = 0.996 + 0.0387;          % water + reservoir dry parts in the pod (kg)
g = 9.81;
W_nosein  = 10*g*m_water_res;          % LC2: 10 g nose-in, bottle base on the front stop (N)
W_grip    = 20.0;                      % LC3: finger squeeze per side (N)
M_tail    = 7.5e3;                     % LC7: boom moment at the bulkhead (N mm), already 5 N x 0.5 m x 3
W_land    = 10*g*m_water_res;          % LC1: 10 g belly landing, payload through the 2 saddles (N)

rows = {};
add = @(rows, name, sig, allow) [rows; {name, sig, allow, allow/sig}];

% 1. Front stop: annular plate, outer edge glued (fixed) a = 52, hole b = 25, ring load at r0 = 32 (bottle base ring)
a = 52; r0 = 32; t = 3;
sig_fs = @(W, t) 3*W/(2*pi*t^2) * (1 + log(a/r0));
rows = add(rows, 'Front stop full 3 mm lite-ply plate (iteration 1)', sig_fs(fos*W_nosein, 3), liteply);
rows = add(rows, 'Front stop full 3 mm balsa (for comparison)',  sig_fs(fos*W_nosein, 3), balsa_T);
% lightened front stop (built): bearing ring r 25..42 on 4 spokes -> continuous beam between spokes, q = W / (2 pi Rm)
Rm = 33.5; sp = 2*pi*Rm/4; q = fos*W_nosein/(2*pi*Rm);
rows = add(rows, 'Front stop ring 17 x 3 lite-ply between 4 spokes', (q*sp^2/12)/(17*3^2/6), liteply);
rows = add(rows, 'Front stop spoke 10 x 3 lite-ply, W/4 at 7.5 mm', (fos*W_nosein/4*7.5)/(10*3^2/6), liteply);

% 2. Side panel, finger squeeze on a 15 mm patch, panel between formers B1 and B2 (67 mm) x 95 mm
b = 67; rp = 7.5;
sig_pt = @(W, t) 3*W/(2*pi*t^2) * ((1+nu)*log(2*b/(pi*rp)) + 1);
rows = add(rows, 'Side 2 x 1.5 balsa cross-laminated (iteration 1)', sig_pt(fos*W_grip, 3.0), balsa_X);
% D-068: inner layer 1.0 mm; in the grip zone the inner layer is 1.0 mm birch ply (carries the vertical direction),
% outer 1.5 balsa along the grain carries the X direction at the outer fibre
rows = add(rows, 'Side grip zone 1.5 balsa + 1.0 birch ply (built)', sig_pt(fos*W_grip, 2.5), balsa_L);
rows = add(rows, 'Side outside grip 1.5 + 1.0 balsa (no point load; hex zone)', sig_pt(fos*W_grip, 2.5), balsa_X);
rows = add(rows, 'Right side servo zone 1.5 balsa only (grip)',    sig_pt(fos*W_grip, 1.5), balsa_L);
rows = add(rows, 'Right side servo zone 1.5 birch ply (grip)',     sig_pt(fos*W_grip, 1.5), birchply);

% 3. U-frame leg (lite-ply 3 mm, 9 mm wide in its plane) as a cantilever from the floor, squeeze at 50 mm,
%    shared with the side panel (assume the frame takes 50 %)
Zleg = 3*9^2/6;
rows = add(rows, 'U-frame leg 3 x 9 lite-ply, full cantilever (iteration 1)', 0.5*fos*W_grip*50/Zleg, liteply);
% built frames: lower corners cut outside a 13 mm band round the bottle (r 43..56), 6 mm floor and side strips.
% squeeze low (Z -100) on the 6 mm side strip: fixed-fixed between the floor strip (Z -109.5) and the band (Z -80.8)
Ls = 29; Zs = 3*6^2/6;
rows = add(rows, 'Frame side strip 3 x 6, fixed-fixed 29 mm (low squeeze)', (0.5*fos*W_grip*Ls/8)/Zs, liteply);
% squeeze at mid-height (Z -64): leg cantilever from the band junction (Z -80.8), lever 17 mm
rows = add(rows, 'Frame leg 3 x 9 from the band junction (mid squeeze)', (0.5*fos*W_grip*17)/Zleg, liteply);

% 4. Aft cone (X 250) bending under the boom moment: floor + deck flanges, 3 mm sides at 60 % solidity (hex)
h = 93; Af = 1.5*90; ts = 3; sol = 0.6;
I = 2*Af*(h/2)^2 + 2*sol*ts*h^3/12;
rows = add(rows, 'Aft cone bending (boom moment, along-grain skins)', fos*M_tail*(h/2)/I, balsa_L);

% 5. Belly landing: payload through saddle 2 (half) into the floor over the 15 mm skid, 12 mm saddle width
A_skid = 15*12;
rows = add(rows, 'Floor crushing over the skid under saddle 2', fos*0.5*W_land/A_skid, balsa_crush);
A_frame = 15*(12+3);   % with frame B4 behind saddle 2 sharing the bearing
rows = add(rows, 'Floor crushing, saddle 2 + frame B4', fos*0.5*W_land/A_frame, balsa_crush);
% D-068: laminated saddles (lite-ply faces + balsa core): bottle bearing on the cradle edge (arc 100 mm x 12 mm, foam tape),
% the balsa core loaded on its edge grain (end-grain-like crushing 3 MPa interp.) -> use the across-thickness value as the bound
rows = add(rows, 'Laminated saddle: bottle bearing on the balsa core edge', fos*0.5*W_land/(100*12), balsa_crush);

fprintf('\n%-55s %10s %10s %8s\n', 'Check (ultimate = 1.5 x limit)', 'sigma MPa', 'allow MPa', 'margin');
for k = 1:size(rows,1)
    fprintf('%-55s %10.2f %10.2f %8.2f %s\n', rows{k,1}, rows{k,2}, rows{k,3}, rows{k,4}, ternary(rows{k,4} >= 1, 'OK', 'LOW'));
end
fprintf('\nLoads: nose-in %.0f N, grip %.0f N per side, boom %.1f N m, landing %.0f N (limit)\n', W_nosein, W_grip, M_tail/1e3, W_land);

function s = ternary(c, a, b)
if c, s = a; else, s = b; end
end
