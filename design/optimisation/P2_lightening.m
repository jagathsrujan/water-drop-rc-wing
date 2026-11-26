% P2 lightening and optimisation study - hand strength checks (rev B Fusion model, P1 decision: 1.5 mm medium balsa,
% 1.5 mm birch ply). Run: run('P2_lightening.m') from design/optimisation; output saved to P2_lightening.txt (evalc).
% Design values and sources: as P1_single_stock.m (references.md R1, R3, R4). Ultimate = 1.5 x limit (D-064).
clear; fos = 1.5; g = 9.81;

%% materials (identical to P1_single_stock.m)
rho_d = 0.12; k = rho_d/0.16; p5 = @(cov) 1 - 1.645*cov;
B.E = 3400*k; B.ET = 0.015*B.E; B.G = 0.037*B.E; B.f = 21.6*k*p5(0.16); B.fT = 0.04*B.f;
B.c = 14.9*k*p5(0.18); B.s = 2.1*k*p5(0.14); B.cp = 21.6*rho_d^2.09*p5(0.28); B.nu = 0.488;   % nu_LT, R1 Table 5-2
H.E = 11000; H.ET = 0.050*H.E; H.G = 0.068*H.E; H.f = 85*p5(0.16); H.fT = 0.04*H.f;            % G_LT/E_L yellow birch
H.c = 39.2*p5(0.18); H.s = 8.3*p5(0.14); H.nu = 0.45;   % nu_LT birch: estimate (R1 Table 5-2 yellow birch row)
C.fc = 200; C.E = 28000;                                % R3 lower bounds
lamA = @(m, t, a) {m, t, a};

%% laminates
L.birch15   = {H,0.5,0; H,0.5,90; H,0.5,0};
L.birch3_par = {H,0.5,0; H,0.5,90; H,0.5,0; H,0.5,0; H,0.5,90; H,0.5,0};    % 2 x 1.5 birch, faces parallel
L.birch3_x  = {H,0.5,0; H,0.5,90; H,0.5,0; H,0.5,90; H,0.5,0; H,0.5,90};    % 2 x 1.5 birch, crossed
L.side_grip = {B,1.5,0; H,0.5,90; H,0.5,0; H,0.5,90};                        % outer balsa (grain X) + birch 1.5 (face vertical)
L.side_bb   = {B,1.5,0; B,1.5,90};                                           % outer + inner balsa 1.5, crossed
L.side_out  = {B,1.5,0};                                                     % outer only (between inner posts)

rows = {};
add = @(rows, part, check, lam, sig, allow) [rows; {part, check, lam, sig, allow, allow/sig}];

%% A. Front stop, nose-in 10 g (D-064 LC2), now 2 x 1.5 birch
m_res = 0.996 + 0.0387; W_nose = 10*g*m_res; Wu = fos*W_nose;
for c = {'birch3_par','birch3_x'}
    lam = L.(c{1}); t = 3.0;
    aw = min(bend_allow(lam,0), bend_allow(lam,90));
    for ns = [4 6]
        for w = [10 14]
            rows = add(rows, 'FS', sprintf('%d spokes %d wide, W/n at 7.5 mm', ns, w), c{1}, (Wu/ns*7.5)/(w*t^2/6), aw);
        end
    end
    a = 52; r0 = 32;                                     % full annular plate, outer edge fixed (strength_estimate.m)
    rows = add(rows, 'FS', 'full plate (no spokes), ring load r 32', c{1}, 3*Wu/(2*pi*t^2)*(1 + log(a/r0)), aw);
end

%% B. Floor crushing at the 10 g belly landing (LC1): saddle foot -> floor -> skid (15 wide)
W_land = 10*g*m_res; F_s = fos*0.5*W_land;              % per saddle, ultimate
rows = add(rows, 'Floor under saddle', 'today: foot 15 long over the skid', 'balsa 1.5', F_s/(15*15), B.cp);
L_req = F_s/(15*B.cp);
fprintf('Floor pad: bearing length needed over the 15 mm skid = %.1f mm (ultimate, margin 1)\n', L_req);
Lp = 40; q = F_s/Lp; ov = (Lp - 15)/2;
rows = add(rows, 'Floor under saddle', 'with 40 x 15 birch 1.5 pad on the floor', 'balsa 1.5', F_s/(15*Lp), B.cp);
rows = add(rows, 'Saddle pad', 'pad 1.5 birch, overhang bending', 'birch15', (q*ov^2/2)/(15*1.5^2/6), bend_allow(L.birch15,0));

%% C. Side grip zone: orthotropic plate (Navier, simply supported - conservative), finger patch 15 x 15, 20 N (LC3)
Wg = fos*20;
for c = {{'side_grip', 67, 95}, {'side_bb', 67, 95}, {'side_out', 20, 95}}
    nm = c{1}{1}; a = c{1}{2}; b = c{1}{3};
    [mg, w0] = navier_patch(L.(nm), a, b, 15, 15, Wg);
    rows = add(rows, 'Side panel', sprintf('Navier %dx%d, patch 15x15 (defl %.1f mm)', a, b, w0), nm, 1, mg);
end

%% D. Booms (LC7): root moment per boom, 10x8 today vs 8x6
M_b = fos*7.5e3/2;  F_tip = (7.5e3/2)/490;              % N mm ult; limit tip-equivalent force (N)
for tb = [10 8; 8 6]'
    Do = tb(1); Di = tb(2); I = pi/64*(Do^4 - Di^4);
    rows = add(rows, 'Boom', sprintf('%dx%d tube, root bending (compression)', Do, Di), 'carbon', M_b*(Do/2)/I, C.fc);
    fprintf('Boom %dx%d: I %.0f mm4, limit tip deflection %.0f mm at E %.0f GPa (R3 lower bound)\n', Do, Di, I, ...
            F_tip*490^3/(3*C.E*I), C.E/1e3);
end

%% E. Wing root shear web (D-004, n 6 ultimate)
V = 6*(0.721 + 0.996)*g/2;
rows = add(rows, 'Wing web', 'root bay web 1 x 1.5', 'balsa', V/(1.5*29), B.s);
rows = add(rows, 'Wing web', 'root bay web 2 x 1.5 (y 0-110)', 'balsa', V/(3.0*29), B.s);

%% F. Aft cone bending with hex holes in the sides (strength_estimate.m case 4, LC7)
h = 93; Af = 1.5*90; ts = 3.0;
for sol = [1.0 0.6]
    I = 2*Af*(h/2)^2 + 2*sol*ts*h^3/12;
    rows = add(rows, 'Aft cone', sprintf('bending, side solidity %.1f, flange compression', sol), 'balsa', fos*7.5e3*(h/2)/I, B.c);
end

%% report
fprintf('\n%-20s %-50s %-11s %9s %9s %7s\n', 'Part', 'Check (ultimate)', 'laminate', 'sigma', 'allow', 'margin');
for i = 1:size(rows,1)
    r = rows(i,:);
    fprintf('%-20s %-50s %-11s %9.2f %9.2f %7.2f %s\n', r{1}, r{2}, r{3}, r{4}, r{5}, r{6}, tern(r{6} >= 1, 'OK', 'LOW'));
end
fprintf('(Navier rows: sigma = 1, allow = margin)\n');

%% ---------------- functions ----------------
function [margin, w0] = navier_patch(lam, a, b, cu, cv, P)
% simply supported orthotropic plate a (x, grain 0) x b (y), centred patch cu x cv, total load P (N).
% classical laminate D matrix (no B coupling assumed for the bending check: conservative estimate for 2-layer
% laminates is avoided by using the bending about the E-weighted neutral plane); first-ply failure per layer.
n = size(lam,1); t = sum([lam{:,2}]); z = [0 cumsum([lam{:,2}])];
Q = zeros(3,3,n);
for i = 1:n
    m = lam{i,1}; E1 = m.E; E2 = m.ET; G12 = m.G; nu12 = m.nu; nu21 = nu12*E2/E1;
    q = [E1 nu12*E2 0; nu12*E2 E2 0; 0 0 G12*(1 - nu12*nu21)]/(1 - nu12*nu21);
    if mod(lam{i,3},180) == 90, q = q([2 1 3],[2 1 3]); end
    Q(:,:,i) = q;
end
zc = 0.5*(z(1:n)+z(2:n+1)); Ex = squeeze(Q(1,1,:))';
zn = sum(Ex.*[lam{:,2}].*zc)/sum(Ex.*[lam{:,2}]);
D = zeros(3);
for i = 1:n, D = D + Q(:,:,i)*((z(i+1)-zn)^3 - (z(i)-zn)^3)/3; end
p0 = P/(cu*cv); w0 = 0; kx = 0; ky = 0; kxy = 0;
x0 = a/2; y0 = b/2;
for mm = 1:2:79
    for nn = 1:2:79
        qmn = 16*p0/(pi^2*mm*nn)*sin(mm*pi/2)*sin(nn*pi/2)*sin(mm*pi*cu/(2*a))*sin(nn*pi*cv/(2*b));
        al = mm*pi/a; be = nn*pi/b;
        den = D(1,1)*al^4 + 2*(D(1,2) + 2*D(3,3))*al^2*be^2 + D(2,2)*be^4;
        Wmn = qmn/den; s = sin(al*x0)*sin(be*y0);
        w0 = w0 + Wmn*s; kx = kx + Wmn*al^2*s; ky = ky + Wmn*be^2*s;
    end
end
margin = inf;
for i = 1:n
    m = lam{i,1}; zz = max(abs(z(i)-zn), abs(z(i+1)-zn));
    st = Q(:,:,i)*[kx; ky; kxy]*zz;                  % stresses in plate axes at the layer's outer fibre
    if mod(lam{i,3},180) == 0, sL = st(1); sT = st(2); else, sL = st(2); sT = st(1); end
    margin = min([margin, m.f/abs(sL), m.fT/abs(sT)]);
end
end

function [a, t] = bend_allow(lam, ang)
n = size(lam,1); t = sum([lam{:,2}]); z = [0 cumsum([lam{:,2}])];
E = zeros(n,1); f = zeros(n,1);
for i = 1:n
    m = lam{i,1}; if mod(lam{i,3} - ang, 180) == 0, E(i) = m.E; f(i) = m.f; else, E(i) = m.ET; f(i) = m.fT; end
end
zc = 0.5*(z(1:n) + z(2:n+1))'; ti = [lam{:,2}]';
zn = sum(E.*ti.*zc)/sum(E.*ti);
EI = sum(E.*(ti.^3/12 + ti.*(zc - zn).^2));
a = 6*min(f.*EI./(E.*max(abs(z(1:n)' - zn), abs(z(2:n+1)' - zn))))/t^2;
end

function s = tern(c, a, b)
if c, s = a; else, s = b; end
end
