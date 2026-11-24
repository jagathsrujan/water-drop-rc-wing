/* 3D view of the build (three.js). Every part is extruded from its real outline (the exact laser loops for laser
   parts) and placed with its frame from the model, so what you see is the model, not a drawing.
   game.js calls View3D.show(scene description); clicks on ghost parts come back through onGhost(itemId). */
(function () {
  "use strict";
  const T = window.THREE;
  const View3D = { ok: false };
  window.View3D = View3D;
  if (!T || !T.WebGLRenderer) return;

  const COLOR = {
    balsa_light: 0xf1e2bf, balsa_med: 0xe3c58a, balsa_hard: 0xd2a862, ply: 0xbf9258, liteply: 0xd8bf88,
    petg: 0x6fa8d8, carbon: 0x2e2e2e, steel: 0x9aa0a6, pla_jig: 0xa58be0, elec: 0x48505c, pet: 0xf2f4f6,
    birch: 0xc79c62, "pet bottle": 0xbfe1f5,
  };
  let renderer, scene, camera, controls, box, tip, canvasWrap;
  let geomCache = {};
  let ghostMeshes = [];
  let partMeshes = [];
  let anims = [];
  let needs = true;
  let last = null;
  let lastFitKey = "";
  const ray = new T.Raycaster();
  const mouse = new T.Vector2();

  View3D.init = function (wrap) {
    try {
      renderer = new T.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    } catch (e) { return false; }
    if (!renderer.getContext()) return false;
    canvasWrap = wrap;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0xf7f5ef);
    wrap.appendChild(renderer.domElement);
    renderer.domElement.className = "gl";
    scene = new T.Scene();
    camera = new T.PerspectiveCamera(35, 1, 1, 20000);
    camera.up.set(0, 0, 1);
    scene.add(new T.HemisphereLight(0xffffff, 0x8a8170, 1.6));
    const sun = new T.DirectionalLight(0xffffff, 1.6);
    sun.position.set(-400, -600, 900);
    scene.add(sun);
    const fill = new T.DirectionalLight(0xffffff, 0.6);
    fill.position.set(500, 400, 200);
    scene.add(fill);
    controls = new T.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.12;
    controls.addEventListener("change", () => { needs = true; });
    tip = document.createElement("div");
    tip.className = "tip3d hidden";
    wrap.appendChild(tip);
    let down = null;
    renderer.domElement.addEventListener("pointerdown", (e) => { down = [e.clientX, e.clientY]; });
    renderer.domElement.addEventListener("pointerup", (e) => {
      if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
      const hit = pick(e, ghostMeshes);
      if (hit && View3D.onGhost) View3D.onGhost(hit.object.userData.item);
      else if (View3D.onEmpty) View3D.onEmpty();
    });
    renderer.domElement.addEventListener("pointermove", (e) => {
      const g = pick(e, ghostMeshes);
      ghostMeshes.forEach((m) => setHot(m, g && m.userData.item === g.object.userData.item));
      const p = g || pick(e, partMeshes);
      if (p) {
        const r = canvasWrap.getBoundingClientRect();
        tip.textContent = g ? (View3D.ghostTip ? View3D.ghostTip(g.object.userData) : "?") : p.object.userData.name + (p.object.userData.mat ? " · " + p.object.userData.mat : "");
        tip.style.left = (e.clientX - r.left + 12) + "px";
        tip.style.top = (e.clientY - r.top + 12) + "px";
        tip.classList.remove("hidden");
      } else tip.classList.add("hidden");
      renderer.domElement.style.cursor = g ? "pointer" : "grab";
      needs = true;
    });
    renderer.domElement.addEventListener("pointerleave", () => tip.classList.add("hidden"));
    window.addEventListener("resize", resize);
    resize();
    loop();
    View3D.ok = true;
    return true;
  };

  function setHot(m, on) {
    if (m.userData.hot === on) return;
    m.userData.hot = on;
    m.material.opacity = on ? 0.55 : m.userData.baseOpacity;
    needs = true;
  }

  function pick(e, list) {
    const r = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    mouse.y = -((e.clientY - r.top) / r.height) * 2 + 1;
    ray.setFromCamera(mouse, camera);
    const hits = ray.intersectObjects(list, false);
    return hits.length ? hits[0] : null;
  }

  function resize() {
    if (!renderer) return;
    const w = canvasWrap.clientWidth, h = canvasWrap.clientHeight;
    renderer.setSize(w, h, false);
    renderer.domElement.style.width = w + "px";
    renderer.domElement.style.height = h + "px";
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
    needs = true;
  }
  View3D.resize = resize;

  function loop(t) {
    requestAnimationFrame(loop);
    if (anims.length) {
      const now = performance.now();
      anims = anims.filter((a) => {
        const k = Math.min(1, (now - a.t0) / a.dur);
        const e = 1 - Math.pow(1 - k, 3);
        a.obj.position.copy(a.from).lerp(a.to, e);
        return k < 1;
      });
      needs = true;
    }
    if (controls.update()) needs = true;
    if (needs) { renderer.render(scene, camera); needs = false; }
  }

  // ---------------------------------------------------------------- geometry
  function frameMatrix(p, wingToAir) {
    const f = p.frame;
    const m = new T.Matrix4();
    const o = new T.Vector3(f[0][0], f[0][1], f[0][2]).addScaledVector(new T.Vector3(f[3][0], f[3][1], f[3][2]), p.z0 || 0);
    m.makeBasis(new T.Vector3(...f[1]), new T.Vector3(...f[2]), new T.Vector3(...f[3]));
    m.setPosition(o);
    if (wingToAir) m.premultiply(incidence());
    return m;
  }
  function incidence() {
    return new T.Matrix4().makeRotationY(window.KIT.meta.incidence * Math.PI / 180);
  }

  function loopsOf(p) {
    if (p.loops) return p.loops.map((l) => ({ outer: l.outer, pts: l.pts }));
    const out = [{ outer: true, pts: p.outline }];
    (p.holes || []).forEach((h) => {
      if (h[0] === "c") {
        const pts = [];
        for (let i = 0; i < 28; i++) { const a = i / 28 * 2 * Math.PI; pts.push([h[1] + h[3] * Math.cos(a), h[2] + h[3] * Math.sin(a)]); }
        out.push({ outer: false, pts });
      } else out.push({ outer: false, pts: h[1] });
    });
    return out;
  }

  function plateGeometry(name, p) {
    if (geomCache[name]) return geomCache[name];
    const loops = loopsOf(p);
    const outer = loops.find((l) => l.outer) || loops[0];
    const shape = new T.Shape(outer.pts.map((q) => new T.Vector2(q[0], q[1])));
    const ob = bounds(outer.pts);
    loops.forEach((l) => {
      if (l === outer || l.pts.length < 3) return;
      const b = bounds(l.pts);
      // only real holes (inside the outer outline); cutters that cross the edge are already in the outline
      if (b[0] < ob[0] - 0.01 || b[1] < ob[1] - 0.01 || b[2] > ob[2] + 0.01 || b[3] > ob[3] + 0.01) return;
      shape.holes.push(new T.Path(l.pts.map((q) => new T.Vector2(q[0], q[1]))));
    });
    let g;
    try {
      g = new T.ExtrudeGeometry(shape, { depth: p.t, bevelEnabled: false, curveSegments: 4 });
    } catch (e) {
      g = new T.ExtrudeGeometry(new T.Shape(outer.pts.map((q) => new T.Vector2(q[0], q[1]))), { depth: p.t, bevelEnabled: false });
    }
    g.computeVertexNormals();
    geomCache[name] = g;
    return g;
  }
  function bounds(pts) {
    const b = [1e9, 1e9, -1e9, -1e9];
    pts.forEach((q) => { b[0] = Math.min(b[0], q[0]); b[1] = Math.min(b[1], q[1]); b[2] = Math.max(b[2], q[0]); b[3] = Math.max(b[3], q[1]); });
    return b;
  }

  function meshFor(name, p, wingToAir, mat) {
    if (p.frame) {
      const m = new T.Mesh(plateGeometry(name, p), mat);
      m.applyMatrix4(frameMatrix(p, wingToAir));
      return m;
    }
    if (p.p0) {
      const a = new T.Vector3(...p.p0), b = new T.Vector3(...p.p1);
      if (wingToAir) { a.applyMatrix4(incidence()); b.applyMatrix4(incidence()); }
      const L = a.distanceTo(b);
      const g = new T.CylinderGeometry(Math.max(p.r, 0.5), Math.max(p.r, 0.5), Math.max(L, 0.5), 16);
      const m = new T.Mesh(g, mat);
      m.position.copy(a).add(b).multiplyScalar(0.5);
      m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), b.clone().sub(a).normalize());
      m.updateMatrix();
      return m;
    }
    if (p.box) {
      const b = p.box;
      const g = new T.BoxGeometry(b[1] - b[0], b[3] - b[2], b[5] - b[4]);
      const m = new T.Mesh(g, mat);
      m.position.set((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2);
      if (wingToAir) { m.position.applyMatrix4(incidence()); m.rotation.y = window.KIT.meta.incidence * Math.PI / 180; }
      return m;
    }
    return null;
  }

  const matCache = {};
  function partMaterial(p, now) {
    const key = p.mat + (now ? ":now" : "");
    if (!matCache[key]) {
      const col = COLOR[p.mat] || 0xcccccc;
      const transparent = p.mat === "pla_jig" || p.mat === "pet bottle" || p.mat === "pet";
      matCache[key] = new T.MeshStandardMaterial({
        color: col, roughness: p.mat === "carbon" ? 0.45 : 0.85, metalness: p.mat === "steel" ? 0.6 : 0.0,
        transparent, opacity: p.mat === "pet bottle" ? 0.35 : (transparent ? 0.8 : 1), side: T.DoubleSide,
        emissive: now ? 0x10305a : 0x000000, emissiveIntensity: now ? 0.35 : 0,
      });
    }
    return matCache[key];
  }
  const ghostMat = (hint) => new T.MeshBasicMaterial({ color: hint ? 0xf0a800 : 0x1a73d9, transparent: true, opacity: hint ? 0.45 : 0.18, depthWrite: false, side: T.DoubleSide });
  const propMat = new T.MeshStandardMaterial({ color: 0x333333, transparent: true, opacity: 0.18, depthWrite: false, side: T.DoubleSide });
  const edgeMat = new T.LineBasicMaterial({ color: 0x5b4a2c, transparent: true, opacity: 0.55 });
  const ghostEdge = new T.LineBasicMaterial({ color: 0x1a73d9 });
  const edgeCache = {};

  // ---------------------------------------------------------------- scene
  /* desc: {key, space ('air'|'wing'|'all'), placed: [{name, now, fresh}], ghosts: [{name, item, hint}],
            pins: [[x,y,z0,z1]], dir: [x,y,z], up, fit: 'step'|'all', fitKey} */
  View3D.show = function (desc) {
    const P = window.KIT.parts;
    // clear
    [...partMeshes, ...ghostMeshes].forEach((m) => { scene.remove(m); if (m.userData.own) m.geometry.dispose(); });
    scene.children.filter((c) => c.userData && c.userData.tmp).forEach((c) => scene.remove(c));
    partMeshes = []; ghostMeshes = [];
    const wingToAir = (p) => desc.space === "all" && (p.assembly === "Wing" || p.assembly === "Wing jigs");
    const stepBox = new T.Box3(), allBox = new T.Box3();
    desc.placed.forEach((q) => {
      const p = P[q.name];
      if (!p) return;
      const m = meshFor(q.name, p, wingToAir(p), q.name === "PROP-DISC" ? propMat : partMaterial(p, q.now));
      if (!m) return;
      m.userData = { name: q.name, mat: p.matlabel, tmp: true, own: !p.frame };
      scene.add(m);
      partMeshes.push(m);
      if (p.frame && p.mat !== "pet bottle") {
        const ek = q.name;
        if (!edgeCache[ek]) edgeCache[ek] = new T.EdgesGeometry(m.geometry, 25);
        m.add(new T.LineSegments(edgeCache[ek], edgeMat));
      }
      m.updateMatrixWorld();
      const bb = new T.Box3().setFromObject(m);
      allBox.union(bb);
      if (q.now) stepBox.union(bb);
      if (q.fresh) {
        const to = m.position.clone();
        const from = to.clone().add(new T.Vector3(0, 0, 120));
        m.position.copy(from);
        anims.push({ obj: m, from, to, t0: performance.now(), dur: 450 });
      }
    });
    (desc.pins || []).forEach((pn) => {
      const g = new T.CylinderGeometry(2.95, 2.95, pn[3] - pn[2], 14);
      const m = new T.Mesh(g, partMaterial({ mat: "pla_jig" }, false));
      m.position.set(pn[0], pn[1], (pn[2] + pn[3]) / 2);
      m.rotation.x = Math.PI / 2;
      m.userData = { name: "PIN-6x11", tmp: true, own: true };
      scene.add(m); partMeshes.push(m);
    });
    desc.ghosts.forEach((gq) => {
      const p = P[gq.name];
      if (!p) return;
      const m = meshFor(gq.name, p, wingToAir(p), ghostMat(gq.hint));
      if (!m) return;
      m.userData = { item: gq.item, name: gq.name, tmp: true, own: !p.frame, baseOpacity: gq.hint ? 0.45 : 0.18 };
      m.renderOrder = 2;
      if (p.frame) {
        if (!edgeCache[gq.name]) edgeCache[gq.name] = new T.EdgesGeometry(m.geometry, 25);
        const e = new T.LineSegments(edgeCache[gq.name], gq.hint ? new T.LineBasicMaterial({ color: 0xe09a00 }) : ghostEdge);
        m.add(e);
      }
      scene.add(m);
      ghostMeshes.push(m);
      m.updateMatrixWorld();
      const bb = new T.Box3().setFromObject(m);
      stepBox.union(bb); allBox.union(bb);
    });
    // camera: re-frame when the step or view changes
    const fitKey = desc.fitKey;
    if (fitKey !== lastFitKey) {
      lastFitKey = fitKey;
      const b = desc.fit === "step" && !stepBox.isEmpty() ? stepBox : (!allBox.isEmpty() ? allBox : stepBox);
      frame(b.isEmpty() ? new T.Box3(new T.Vector3(-100, -100, -100), new T.Vector3(100, 100, 100)) : b, desc.dir, desc.up);
    }
    needs = true;
  };

  function frame(b, dir, up) {
    const c = b.getCenter(new T.Vector3());
    const s = b.getSize(new T.Vector3());
    const r = Math.max(s.length() / 2, 40);
    const d = new T.Vector3(...dir).normalize();
    const dist = r / Math.sin((camera.fov * Math.PI / 180) / 2) * 0.95;
    camera.up.set(...(up || [0, 0, 1]));
    camera.position.copy(c).addScaledVector(d, dist);
    camera.near = Math.max(dist / 100, 0.5);
    camera.far = dist * 20;
    camera.updateProjectionMatrix();
    controls.target.copy(c);
    controls.update();
    needs = true;
  }
  View3D.reframe = function () { lastFitKey = ""; };
  View3D.snapshot = function () { renderer.render(scene, camera); return renderer.domElement.toDataURL("image/png"); };
})();
