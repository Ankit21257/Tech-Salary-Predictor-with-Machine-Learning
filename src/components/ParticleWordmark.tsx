import React, { useMemo, type CSSProperties } from "react";

type FocusRole = "background" | "button" | "visual";
type EffectMode = "light" | "dark";

type FocusTarget = {
  selector: string;
  role: FocusRole;
  fit?: "cover" | "contain-square" | "wide-wordmark" | "portrait-stage";
  preserveTransform?: boolean;
};

type EffectDefinition = {
  title: string;
  source: string;
  background: string;
  targets: readonly FocusTarget[];
  theme?: {
    nativeMode?: EffectMode;
    lightBackground: string;
    darkBackground: string;
    invertBackground?: boolean;
  };
  transformSource?: (source: string, mode: EffectMode) => string;
  hiddenTargets?: readonly string[];
};

const TECH_COMPENSATION_WORDMARK_SVG = `<svg width="2400" height="300" viewBox="0 0 2400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
  <text x="1200" y="195" text-anchor="middle" fill="#F4F4F0" font-family="'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="125" font-weight="900" letter-spacing="-2">TECH COMPENSATION PREDICTOR</text>
</svg>`;

export type NeuformIsolatedEffectProps = {
  mode?: EffectMode;
  hue?: number;
  saturation?: number;
  brightness?: number;
  className?: string;
  style?: CSSProperties;
};

export const NEUFORM_ISOLATED_DEFAULTS = {
  mode: "dark",
  hue: 0,
  saturation: 1,
  brightness: 1,
} as const;

function transformEpiludeWordmarkSource(source: string, mode: EffectMode) {
  const palette =
    mode === "light"
      ? "[[8, 10, 15], [40, 48, 62], [85, 96, 116]]"
      : "[[255, 255, 255], [226, 232, 240], [191, 205, 225]]";

  return source
    .replace(
      "<title>Epilude — Footer</title>",
      "<title>Tech Compensation Predictor Particle Wordmark</title>",
    )
    .replace(
      "aspect-ratio: 8.541554959785524;",
      "aspect-ratio: 8.0;",
    )
    .replace(
      /var WORDMARK =[\s\S]*?"<\/svg>";/,
      `var WORDMARK = ${JSON.stringify(TECH_COMPENSATION_WORDMARK_SVG)};`,
    )
    .replace(
      "var PALETTE = [[255, 255, 255], [226, 232, 240], [191, 205, 225]];",
      `var PALETTE = ${palette};`,
    )
    .replace(
      "a: 0.04 + 0.95 * band * Math.pow(flake, 1.8)",
      "a: 0.14 + 0.86 * band * Math.pow(flake, 1.8)",
    );
}

const epiludeFooterSource = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Epilude — Footer</title>
<style>
  :root {
    --olive-400: #a9a9ac;
    --olive-500: #7a7a7d;
    --olive-950: #0c0c0d;
    --white: #fff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    background: transparent;
    color: var(--white);
    min-height: 100%;
  }
  body {
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
  }

  .storm-wrap {
    width: 100%;
    user-select: none;
    -webkit-user-select: none;
  }
  .storm {
    position: relative;
    overflow: hidden;
    width: 100%;
    aspect-ratio: 8.0;
  }
  .storm canvas { display: block; width: 100%; height: 100%; }
</style>
</head>
<body>
  <div class="storm-wrap" aria-hidden="true">
    <div class="storm" id="storm">
      <canvas id="storm-canvas"></canvas>
    </div>
  </div>

<script>
(function () {
  var WORDMARK = ${JSON.stringify(TECH_COMPENSATION_WORDMARK_SVG)};

  var PALETTE = [[255, 255, 255], [226, 232, 240], [191, 205, 225]];
  var FORMATS = ["dot", "dot", "square"];
  var SIZE_SMALL = [1.4, 2.8];
  var SIZE_BIG = [3, 4.2];
  var BIG_CHANCE = 0.07;
  var GAP = 6;
  var SPEED = 2;
  var SEED = 1337;
  var GAMMA = 0.8;
  var DUR = 8;
  var TAU = Math.PI * 2;

  function noise(x, y, t) {
    var a = x + 0.7 * Math.sin(1.2 * y + t);
    var r = y + 0.7 * Math.cos(1.1 * x - t);
    return (Math.sin(1.3 * a + 0.6 * t) + Math.cos(1.5 * r - 0.5 * t) + Math.sin((a + r) * 0.9 + 0.3 * t)) / 3;
  }

  function snowfall(p, t, n) {
    var swirl = n.swirl ? n.swirl * noise(3 * p.nx, 3 * p.ny, 0.5 * t) : 0;
    var sway = (n.sway || 0) * Math.sin(0.8 * t + p.offset * TAU + 4 * p.ny) + swirl;
    var i = n.axis === "x" ? p.nx : p.ny;
    var l = n.axis === "x" ? p.ny : p.nx;
    var o = i * n.freq - t * n.fall + p.offset * n.freq + sway + (n.wind || 0) * l;
    var s = o - Math.floor(o);
    return s < n.trail ? 1 - s / n.trail : 0;
  }

  function squall(p, t) {
    var band = 0.35 + 0.65 * Math.pow(0.5 + 0.5 * Math.sin(3 * p.nx - 0.5 * t), 2);
    var flake = snowfall(p, t, { fall: 0.26, freq: 5, trail: 0.4, sway: 0.14, wind: 0.8 });
    return {
      a: 0.14 + 0.86 * band * Math.pow(flake, 1.8),
      p: 0.7 * p.offset
    };
  }

  function lerpRGB(a, b, t) {
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  }

  function mixPalette(p) {
    var e = Math.max(0, Math.min(1, p)) * (PALETTE.length - 1);
    var r = Math.floor(e);
    var s = e - r;
    return lerpRGB(PALETTE[r], PALETTE[Math.min(PALETTE.length - 1, r + 1)], s);
  }

  var canvas = document.getElementById("storm-canvas");
  var host = document.getElementById("storm");
  var ctx = canvas.getContext("2d");
  var particles = [];
  var maskImg = null;
  var maskReady = false;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var playing = !reduced;
  var tNow = 0;
  var t0 = performance.now();
  var raf = 0;
  var visible = true;

  function lcg(seed) {
    var e = seed >>> 0;
    return function () {
      e = (1664525 * e + 0x3c6ef35f) >>> 0;
      return e / 0xffffffff;
    };
  }

  function makeMask(w, h) {
    if (!maskImg || !maskReady || !maskImg.width || !maskImg.height) return null;
    var off = document.createElement("canvas");
    off.width = w;
    off.height = h;
    var g = off.getContext("2d");
    if (!g) return null;
    var scale = Math.min(w / maskImg.width, h / maskImg.height);
    var dw = maskImg.width * scale;
    var dh = maskImg.height * scale;
    g.drawImage(maskImg, (w - dw) / 2, (h - dh) / 2, dw, dh);
    var data;
    try { data = g.getImageData(0, 0, w, h).data; }
    catch (e) { return null; }
    return function (x, y) {
      var ix = Math.min(w - 1, Math.max(0, Math.round(x)));
      var iy = Math.min(h - 1, Math.max(0, Math.round(y)));
      var i = (iy * w + ix) * 4;
      var lum = (0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]) / 255;
      return Math.pow(lum * (data[i + 3] / 255), GAMMA);
    };
  }

  function rebuild() {
    var w = host.clientWidth;
    var h = host.clientHeight;
    if (!w || !h) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.max(1, Math.floor(w * dpr));
    canvas.height = Math.max(1, Math.floor(h * dpr));
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    var sample = makeMask(w, h);
    var rand = lcg(SEED);
    var cols = Math.ceil(w / GAP);
    var rows = Math.ceil(h / GAP);
    var ox = (w - (cols - 1) * GAP) / 2;
    var oy = (h - (rows - 1) * GAP) / 2;
    var cx = (cols - 1) / 2;
    var cy = (rows - 1) / 2;
    var maxd = Math.hypot(cx, cy) || 1;
    particles = [];
    for (var y = 0; y < rows; y++) {
      for (var x = 0; x < cols; x++) {
        var format = FORMATS[Math.floor(rand() * FORMATS.length)];
        var range = rand() < BIG_CHANCE ? SIZE_BIG : SIZE_SMALL;
        var size = range[0] + rand() * (range[1] - range[0]);
        var px = ox + x * GAP;
        var py = oy + y * GAP;
        particles.push({
          cx: px,
          cy: py,
          nx: cols > 1 ? x / (cols - 1) : 0.5,
          ny: rows > 1 ? y / (rows - 1) : 0.5,
          dist: Math.hypot(x - cx, y - cy) / maxd,
          format: format,
          size: size,
          phase: rand() * Math.PI * 2,
          speed: 0.6 + 2.6 * rand(),
          offset: rand(),
          mask: sample ? sample(px, py) : 1
        });
      }
    }
  }

  function drawParticle(p, t) {
    var field = squall(p, t);
    var alpha = field.a;
    var rgb = mixPalette(field.p);
    alpha = Math.max(0, Math.min(1, alpha));
    if (p.mask < 1) alpha = p.mask * (0.3 + 0.7 * alpha);
    if (alpha <= 0.005) return;
    ctx.fillStyle = "rgba(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + "," + alpha + ")";
    var hx = p.cx, hy = p.cy, d = p.size, r = d / 2;
    if (p.format === "square") ctx.fillRect(hx - r, hy - r, d, d);
    else {
      ctx.beginPath();
      ctx.arc(hx, hy, r, 0, TAU);
      ctx.fill();
    }
  }

  function render(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < particles.length; i++) drawParticle(particles[i], t);
  }

  function apply(t) {
    tNow = ((t % DUR) + DUR) % DUR;
    render(tNow * SPEED);
  }

  function tick(now) {
    if (playing && visible) {
      tNow = ((now - t0) / 1000) % DUR;
      render(tNow * SPEED);
    }
    raf = requestAnimationFrame(tick);
  }

  function play() {
    playing = true;
    t0 = performance.now() - tNow * 1000;
  }

  function pause() {
    playing = false;
  }

  var img = new Image();
  img.onload = function () {
    maskImg = img;
    maskReady = true;
    rebuild();
    apply(tNow);
  };
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(WORDMARK);

  rebuild();
  apply(0);
  raf = requestAnimationFrame(tick);

  window.addEventListener("resize", function () {
    rebuild();
    apply(tNow);
  });

  if (typeof ResizeObserver !== "undefined") {
    var lastW = host.clientWidth, lastH = host.clientHeight;
    new ResizeObserver(function () {
      if (host.clientWidth !== lastW || host.clientHeight !== lastH) {
        lastW = host.clientWidth;
        lastH = host.clientHeight;
        rebuild();
        apply(tNow);
      }
    }).observe(host);
  }

  if (typeof IntersectionObserver !== "undefined") {
    new IntersectionObserver(function (entries) {
      var on = entries[0] && entries[0].isIntersecting;
      if (on === visible) return;
      visible = !!on;
      if (visible) t0 = performance.now() - tNow * 1000;
    }, { rootMargin: "120px" }).observe(canvas);
  }

  document.addEventListener("visibilitychange", function () {
    if (!document.hidden && playing) t0 = performance.now() - tNow * 1000;
  });

  window.__DUR = DUR;
  window.__seek = function (t) { pause(); apply(t); };
  window.__play = play;
  window.__pause = pause;
  window.__time = function () { return tNow; };
})();
</script>
</body>
</html>`;

const PARTICLE_WORDMARK_EFFECT: EffectDefinition = {
  title: "Tech Compensation Predictor particle wordmark",
  source: epiludeFooterSource,
  background: "transparent",
  theme: {
    lightBackground: "transparent",
    darkBackground: "transparent",
  },
  transformSource: transformEpiludeWordmarkSource,
  targets: [{ selector: "#storm", role: "visual", fit: "wide-wordmark" }],
};

function clamp(value: number, minimum: number, maximum: number) {
  return Math.min(maximum, Math.max(minimum, value));
}

function effectBackground(definition: EffectDefinition, mode: EffectMode) {
  return definition.theme?.[`${mode}Background`] ?? definition.background;
}

function buildFocusedDocument(definition: EffectDefinition, mode: EffectMode) {
  const background = effectBackground(definition, mode);
  const invertBackground =
    definition.theme?.invertBackground === true &&
    definition.theme.nativeMode !== mode;
  const source =
    definition.transformSource?.(definition.source, mode) ?? definition.source;
  const targetJson = JSON.stringify(definition.targets).replace(
    /</g,
    "\\u003c",
  );
  const hiddenTargetJson = JSON.stringify(
    definition.hiddenTargets ?? [],
  ).replace(/</g, "\\u003c");
  const modeJson = JSON.stringify(mode);
  const backgroundFilter = invertBackground
    ? "filter: invert(1) hue-rotate(180deg) saturate(.92) brightness(1.02) !important;"
    : "";
  const focusStyle = `<style data-threeui-focus>
html, body { width: 100% !important; height: 100% !important; min-height: 0 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important; background: ${background} !important; color-scheme: ${mode} !important; }
body { position: relative !important; display: flex !important; align-items: center !important; justify-content: center !important; }
body > * { visibility: hidden !important; }
body[data-threeui-ready] > [data-threeui-role] { visibility: visible !important; }
[data-threeui-residual] { display: none !important; }
[data-threeui-hidden] { display: none !important; }
[data-threeui-role="background"] { position: fixed !important; inset: 0 !important; width: 100% !important; height: 100% !important; max-width: none !important; max-height: none !important; z-index: 0 !important; opacity: 1 !important; pointer-events: none !important; ${backgroundFilter} }
[data-threeui-role="button"] { position: relative !important; z-index: 2 !important; opacity: 1 !important; flex: none !important; }
[data-threeui-role="visual"] { position: relative !important; z-index: 1 !important; width: 100% !important; max-width: 100% !important; margin: auto !important; opacity: 1 !important; filter: none !important; }
[data-threeui-role="visual"][data-threeui-fit="wide-wordmark"] { width: 100% !important; max-width: 100% !important; height: auto !important; aspect-ratio: 8 / 1 !important; padding: 0 !important; overflow: hidden !important; }
</style>`;
  const focusScript = `<script data-threeui-focus>
(function () {
  document.documentElement.dataset.sfMode = ${modeJson};
  var isolated = false;
  function isolate() {
    if (isolated) return;
    var specs = ${targetJson};
    var hiddenSelectors = ${hiddenTargetJson};
    var roots = [];
    hiddenSelectors.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (element) {
        element.setAttribute('data-threeui-hidden', '');
        element.setAttribute('aria-hidden', 'true');
        if ('inert' in element) element.inert = true;
      });
    });
    specs.forEach(function (spec) {
      var element = document.querySelector(spec.selector);
      if (!element) return;
      element.setAttribute('data-threeui-role', spec.role);
      if (spec.fit) element.setAttribute('data-threeui-fit', spec.fit);
      if (spec.preserveTransform) element.setAttribute('data-threeui-preserve-transform', '');
      if (!roots.some(function (root) { return root.contains(element); })) roots.push(element);
    });
    if (!roots.length) return;
    isolated = true;
    roots.forEach(function (root) {
      document.body.appendChild(root);
    });
    Array.from(document.body.children).forEach(function (element) {
      if (roots.indexOf(element) !== -1) return;
      element.setAttribute('data-threeui-residual', '');
      element.setAttribute('aria-hidden', 'true');
      if ('inert' in element) element.inert = true;
    });
    document.body.setAttribute('data-threeui-ready', '');
    requestAnimationFrame(function () { window.dispatchEvent(new Event('resize')); });
  }
  function scheduleIsolation() { setTimeout(isolate, 100); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scheduleIsolation, { once: true });
  else scheduleIsolation();
  window.addEventListener("load", isolate, { once: true });
})();
</script>`;
  return source
    .replace(/<\/head>/i, `${focusStyle}</head>`)
    .replace(/<\/body>/i, `${focusScript}</body>`);
}

function NeuformIsolatedEffect({
  definition,
  mode = NEUFORM_ISOLATED_DEFAULTS.mode,
  hue = NEUFORM_ISOLATED_DEFAULTS.hue,
  saturation = NEUFORM_ISOLATED_DEFAULTS.saturation,
  brightness = NEUFORM_ISOLATED_DEFAULTS.brightness,
  className,
  style,
}: NeuformIsolatedEffectProps & { definition: EffectDefinition }) {
  const safeMode: EffectMode = mode === "light" ? "light" : "dark";
  const background = effectBackground(definition, safeMode);
  const source = useMemo(
    () => buildFocusedDocument(definition, safeMode),
    [definition, safeMode],
  );
  const safeHue = clamp(hue, -180, 180);
  const safeSaturation = clamp(saturation, 0, 2);
  const safeBrightness = clamp(brightness, 0.35, 1.65);
  const filter =
    safeHue === 0 && safeSaturation === 1 && safeBrightness === 1
      ? undefined
      : `hue-rotate(${safeHue}deg) saturate(${safeSaturation}) brightness(${safeBrightness})`;

  return (
    <iframe
      className={className}
      data-mode={safeMode}
      title={definition.title}
      srcDoc={source}
      sandbox="allow-scripts"
      loading="eager"
      style={{
        display: "block",
        width: "100%",
        height: "100%",
        border: 0,
        background,
        filter,
        ...style,
      }}
    />
  );
}

export default function ParticleWordmark(props: NeuformIsolatedEffectProps) {
  return (
    <NeuformIsolatedEffect {...props} definition={PARTICLE_WORDMARK_EFFECT} />
  );
}
