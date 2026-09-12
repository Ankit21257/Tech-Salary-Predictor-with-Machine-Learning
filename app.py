import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import io
import time
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))



# Streamlit Page Setup
st.set_page_config(
    page_title="Tech Salary Predictor | Quantum Swarm & Particle Wordmark",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------
# 1. QUANTUM SWARM INTERACTIVE CANVAS BACKGROUND
# --------------------------------------------------------
QUANTUM_SWARM_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
        width: 100%; height: 100%; overflow: hidden;
        background: #09090b; color: #f4f4f5;
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        pointer-events: none;
    }
    #canvas-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0;
        background-color: #09090b;
        pointer-events: none;
    }
    canvas {
        display: block;
        width: 100%; height: 100%;
        cursor: crosshair;
        pointer-events: none;
    }
    .status-badge {
        position: fixed;
        top: 16px;
        left: 20px;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #94a3b8;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        pointer-events: auto;
    }
    .ping-dot {
        position: relative;
        display: flex;
        width: 8px;
        height: 8px;
    }
    .ping-dot .ping {
        position: absolute;
        width: 100%; height: 100%;
        border-radius: 50%;
        background-color: #38bdf8;
        opacity: 0.75;
        animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
    }
    .ping-dot .dot {
        position: relative;
        width: 8px; height: 8px;
        border-radius: 50%;
        background-color: #38bdf8;
    }
    @keyframes ping {
        75%, 100% { transform: scale(2); opacity: 0; }
    }
</style>
</head>
<body>
<div id="canvas-container">
    <canvas id="swarm-canvas"></canvas>
    
    <div class="status-badge">
        <div class="ping-dot">
            <span class="ping" id="ping-span"></span>
            <span class="dot"></span>
        </div>
        <span>SWARM DYNAMICS</span>
    </div>
</div>

<script>
(function() {
    const canvas = document.getElementById("swarm-canvas");
    const ctx = canvas.getContext("2d", { alpha: false });
    
    let isRunning = true;
    const particleCount = 280;
    
    const pointer = {
        x: -2000,
        y: -2000,
        isDown: false,
        radius: 150,
        shockwaves: []
    };
    
    let particles = [];
    const dimensions = { width: 0, height: 0, cx: 0, cy: 0 };
    
    function buildSwarm() {
        const { width, height, cx, cy } = dimensions;
        if (width === 0 || height === 0) return;
        
        particles = [];
        const goldenRatio = (1 + Math.sqrt(5)) / 2;
        const angleIncrement = Math.PI * 2 * goldenRatio;
        const maxRadius = Math.max(width, height) * 0.45;
        
        for (let i = 0; i < particleCount; i++) {
            const dst = Math.pow(i / (particleCount - 1), 0.6) * maxRadius;
            const angle = i * angleIncrement;
            particles.push({
                x: cx + Math.cos(angle) * dst,
                y: cy + Math.sin(angle) * dst,
                vx: 0,
                vy: 0,
                baseX: 0,
                baseY: 0,
                angle: angle,
                distance: dst,
                size: Math.random() * 1.5 + 0.5,
                excitation: 0
            });
        }
    }
    
    const parentWin = (window.parent && window.parent !== window) ? window.parent : window;
    
    function resize() {
        const w = parentWin.innerWidth || window.innerWidth;
        const h = parentWin.innerHeight || window.innerHeight;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        
        dimensions.width = w;
        dimensions.height = h;
        dimensions.cx = w / 2;
        dimensions.cy = h / 2;
        
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = w + "px";
        canvas.style.height = h + "px";
        
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);
        buildSwarm();
    }
    
    parentWin.addEventListener("resize", resize);
    window.addEventListener("resize", resize);
    resize();
    
    let animId = 0;
    let time = 0;
    
    function loop() {
        if (!isRunning) {
            animId = requestAnimationFrame(loop);
            return;
        }
        
        time += 0.002;
        const { width, height, cx, cy } = dimensions;
        
        const bgColor = "#09090b";
        const strokeBase = "71, 85, 105";
        const particleBaseColor = "#475569";
        
        // 1. Clear Background
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, width, height);
        
        // 2. Shockwaves Pass
        for (let s = pointer.shockwaves.length - 1; s >= 0; s--) {
            const sw = pointer.shockwaves[s];
            sw.radius += 15;
            sw.strength *= 0.92;
            if (sw.radius > sw.maxRadius || sw.strength < 0.01) {
                pointer.shockwaves.splice(s, 1);
            }
        }
        
        // 3. Physics Pass
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            
            const currentAngle = p.angle + time * (1 + 100 / (p.distance + 100));
            p.baseX = cx + Math.cos(currentAngle) * p.distance;
            p.baseY = cy + Math.sin(currentAngle) * p.distance;
            
            // a. Spring force
            const dxBase = p.baseX - p.x;
            const dyBase = p.baseY - p.y;
            p.vx += dxBase * 0.02;
            p.vy += dyBase * 0.02;
            
            // b. Pointer interaction
            const dxPointer = p.x - pointer.x;
            const dyPointer = p.y - pointer.y;
            const distPointer = Math.sqrt(dxPointer * dxPointer + dyPointer * dyPointer);
            
            if (distPointer < pointer.radius && distPointer > 0) {
                const force = (pointer.radius - distPointer) / pointer.radius;
                const directionMultiplier = pointer.isDown ? -0.5 : 1.5;
                p.vx += (dxPointer / distPointer) * force * directionMultiplier;
                p.vy += (dyPointer / distPointer) * force * directionMultiplier;
                p.excitation = Math.max(p.excitation, force);
            }
            
            // c. Shockwaves force
            for (let s = 0; s < pointer.shockwaves.length; s++) {
                const sw = pointer.shockwaves[s];
                const dxSw = p.x - sw.x;
                const dySw = p.y - sw.y;
                const distSw = Math.sqrt(dxSw * dxSw + dySw * dySw);
                const ringDelta = Math.abs(distSw - sw.radius);
                
                if (ringDelta < 30) {
                    const impulse = (1 - ringDelta / 30) * sw.strength * 15;
                    p.vx += (dxSw / distSw) * impulse;
                    p.vy += (dySw / distSw) * impulse;
                    p.excitation = Math.max(p.excitation, 1.0);
                }
            }
            
            // d. Friction and movement
            p.vx *= 0.88;
            p.vy *= 0.88;
            p.x += p.vx;
            p.y += p.vy;
            
            // e. Decay excitation
            p.excitation *= 0.95;
        }
        
        // 4. Constellation Lines Pass
        const connectionDistanceSq = 3600;
        ctx.lineWidth = 0.6;
        
        for (let i = 0; i < particles.length; i++) {
            const p1 = particles[i];
            const limit = Math.min(particles.length, i + 15);
            
            for (let j = i + 1; j < limit; j++) {
                const p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distSq = dx * dx + dy * dy;
                
                if (distSq < connectionDistanceSq) {
                    const dist = Math.sqrt(distSq);
                    const opacity = 1 - (dist / 60);
                    const combinedExcitation = Math.max(p1.excitation, p2.excitation);
                    const dynamicAlpha = Math.min(1, (opacity * 0.2) + (combinedExcitation * 0.5));
                    
                    ctx.strokeStyle = `rgba(${strokeBase}, ${dynamicAlpha})`;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        
        // 5. Particles Pass
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            const radius = p.size + (p.excitation * 2.5);
            ctx.fillStyle = particleBaseColor;
            
            if (p.excitation > 0.3) {
                ctx.save();
                ctx.globalAlpha = p.excitation * 0.4;
                ctx.beginPath();
                ctx.arc(p.x, p.y, radius * 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
        
        animId = requestAnimationFrame(loop);
    }
    
    animId = requestAnimationFrame(loop);
    
    // Pointer Event Listeners
    function onPointerMove(e) {
        pointer.x = e.clientX;
        pointer.y = e.clientY;
    }
    function onPointerDown(e) {
        pointer.isDown = true;
        pointer.shockwaves.push({
            x: e.clientX,
            y: e.clientY,
            radius: 10,
            maxRadius: 200,
            strength: 0.8
        });
    }
    function onPointerUp() {
        pointer.isDown = false;
    }
    function onPointerLeave() {
        pointer.x = -2000;
        pointer.y = -2000;
        pointer.isDown = false;
    }
    
    try {
        parentWin.addEventListener("mousemove", onPointerMove, { passive: true });
        parentWin.addEventListener("mousedown", onPointerDown, { passive: true });
        parentWin.addEventListener("mouseup", onPointerUp, { passive: true });
        parentWin.addEventListener("mouseleave", onPointerLeave, { passive: true });
    } catch(e) {
        window.addEventListener("mousemove", onPointerMove, { passive: true });
        window.addEventListener("mousedown", onPointerDown, { passive: true });
        window.addEventListener("mouseup", onPointerUp, { passive: true });
        window.addEventListener("mouseleave", onPointerLeave, { passive: true });
    }
    
})();
</script>
</body>
</html>
"""

st.components.v1.html(QUANTUM_SWARM_HTML, height=0)

# Custom minimal CSS for sleek engineering dashboard with Quantum Swarm canvas background
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Make Streamlit background completely transparent to expose Quantum Swarm canvas */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: transparent !important;
        color: #f8fafc !important;
    }

    /* Keep Streamlit Main Menu Visible */
    #MainMenu {
        visibility: visible !important;
        display: block !important;
    }

    /* Hide ONLY 'Made with Streamlit' footer and brand attribution */
    footer, [data-testid="stFooter"], div[class*="viewerBadge"], [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* Target Made with Streamlit link/badge inside main menu popover */
    ul[data-testid="main-menu-popover"] li:has(a[href*="streamlit.io"]),
    div[data-baseweb="popover"] footer,
    div[data-baseweb="popover"] a[href*="streamlit.io"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Position Quantum Swarm iframe as fixed background */
    iframe, iframe[title*="st"], [data-testid="stIFrame"] iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 0 !important;
        border: none !important;
        pointer-events: none !important;
    }

    /* Glassmorphic Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(9, 9, 11, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    .output-card {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 0.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .salary-main {
        font-size: 2.3rem;
        font-weight: 800;
        color: #38bdf8;
        margin: 0.3rem 0;
        text-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
    }

    .salary-sub {
        font-size: 0.92rem;
        color: #cbd5e1;
    }

    div[data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    /* Refined Button Styling */
    div.stButton > button {
        position: relative;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid rgba(56, 189, 248, 0.5);
        font-size: 13px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1.5px;
        background: rgba(15, 23, 42, 0.85);
        color: #ffffff !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
        transition: all 0.25s ease-in-out;
        width: 100%;
    }

    div.stButton > button:hover {
        background: rgba(56, 189, 248, 0.25);
        color: #ffffff !important;
        border-color: #38bdf8;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
        transform: translateY(-1px);
    }

    /* Custom Styling for Radio Options */
    div[data-testid="stRadio"] > label {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        flex-wrap: wrap;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 10px 18px;
        border-radius: 8px;
        cursor: pointer;
        backdrop-filter: blur(8px);
        transition: all 0.25s ease-in-out;
        color: #f1f5f9 !important;
        display: flex;
        align-items: center;
        margin: 0 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        border-color: #38bdf8;
        background: rgba(30, 41, 59, 0.85);
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
    }

</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "salary_data_multifeature.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(__file__), "models", "salary_model_pipeline.joblib")
    if os.path.exists(path):
        return joblib.load(path)
    return None

df = load_data()
model = load_model()

if df is None:
    st.error("Dataset not found. Ensure `data/salary_data_multifeature.csv` exists.")
    st.stop()

# Header Section with Interactive Dancing Letters Animation
DANCING_LETTERS_HEADER_HTML = """
<style>
    .dancing-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex-wrap: wrap;
        perspective: 1000px;
        user-select: none;
        padding: 0.3rem 0;
        margin-bottom: 0.2rem;
    }
    .dancing-word {
        display: inline-flex;
        margin-right: 0.75rem;
    }
    .dancing-letter {
        position: relative;
        display: inline-block;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        cursor: pointer;
        letter-spacing: -0.02em;
        transform-style: preserve-3d;
        transition: color 0.2s ease, text-shadow 0.2s ease;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
    }
    .dancing-letter:hover {
        color: #38bdf8;
        text-shadow: 0 0 25px rgba(56, 189, 248, 0.8);
    }

    /* 1. Rubber Band (Snap) */
    @keyframes anim-0 {
        0% { transform: scale(1,1); }
        15% { transform: scale(1.25, 0.75); }
        30% { transform: scale(0.75, 1.25); }
        45% { transform: scale(1.15, 0.85); }
        65% { transform: scale(0.95, 1.05); }
        80% { transform: scale(1.05, 0.95); }
        100% { transform: scale(1,1); }
    }
    .anim-0 { animation: anim-0 0.8s ease-in-out; transform-origin: center center; z-index: 10; }

    /* 2. The Hinge */
    @keyframes anim-1 {
        0% { transform: rotate(0deg) translateY(0); }
        20% { transform: rotate(80deg) translateY(10px); }
        40% { transform: rotate(60deg) translateY(-5px); }
        60% { transform: rotate(80deg) translateY(5px); }
        80% { transform: rotate(60deg) translateY(-2px); }
        100% { transform: rotate(0deg) translateY(0); }
    }
    .anim-1 { animation: anim-1 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform-origin: bottom left; z-index: 10; }

    /* 3. Squash and Jump */
    @keyframes anim-2 {
        0% { transform: scaleY(1) translateY(0); }
        30% { transform: scaleY(0.6) translateY(15px); }
        60% { transform: scaleY(1.2) translateY(-30px); }
        100% { transform: scaleY(1) translateY(0); }
    }
    .anim-2 { animation: anim-2 0.6s ease-out; transform-origin: bottom center; z-index: 10; }

    /* 4. Falling Flip */
    @keyframes anim-3 {
        0% { transform: rotateX(0deg) scale(1); }
        15% { transform: rotateX(240deg) scale(1.1); }
        30% { transform: rotateX(150deg) scale(1); }
        45% { transform: rotateX(200deg) scale(1); }
        60% { transform: rotateX(175deg); }
        75% { transform: rotateX(180deg); }
        100% { transform: rotateX(0deg) scale(1); }
    }
    .anim-3 { animation: anim-3 1.8s ease-out; transform-origin: 50% 80%; z-index: 10; }

    /* 5. Elastic Slide */
    @keyframes anim-4 {
        0% { transform: translateX(0); }
        20% { transform: translateX(-18px); }
        40% { transform: translateX(14px); }
        60% { transform: translateX(-8px); }
        80% { transform: translateX(4px); }
        100% { transform: translateX(0); }
    }
    .anim-4 { animation: anim-4 0.8s ease-in-out; transform-origin: center center; z-index: 10; }

    /* 6. Impact Shake */
    @keyframes anim-5 {
        0% { transform: translate(0,0) rotate(0deg); }
        20% { transform: translate(-5px, -2px) rotate(-2deg); }
        40% { transform: translate(5px, 2px) rotate(2deg); }
        60% { transform: translate(-3px, -1px) rotate(-1deg); }
        80% { transform: translate(3px, 1px) rotate(1deg); }
        100% { transform: translate(0,0) rotate(0deg); }
    }
    .anim-5 { animation: anim-5 0.5s linear; transform-origin: center center; z-index: 10; }

    /* 7. Pop Scale */
    @keyframes anim-6 {
        0% { transform: scale(1); }
        50% { transform: scale(1.4); }
        100% { transform: scale(1); }
    }
    .anim-6 { animation: anim-6 0.5s ease-in-out; transform-origin: center center; z-index: 10; }

    /* 8. Levitate */
    @keyframes anim-7 {
        0% { transform: translateY(0) scale(1); text-shadow: 0 0 0 rgba(56,189,248,0); }
        50% { transform: translateY(-25px) scale(1.15); text-shadow: 0 15px 25px rgba(56,189,248,0.7); }
        100% { transform: translateY(0) scale(1); text-shadow: 0 0 0 rgba(56,189,248,0); }
    }
    .anim-7 { animation: anim-7 1.2s ease-in-out; transform-origin: center center; z-index: 10; }

    /* Continuous Dancing while Hovering (infinite loops per physics style) */
    .dancing-letter.l-0:hover { animation: anim-0 0.8s ease-in-out infinite !important; transform-origin: center center; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-1:hover { animation: anim-1 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) infinite !important; transform-origin: bottom left; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-2:hover { animation: anim-2 0.6s ease-out infinite !important; transform-origin: bottom center; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-3:hover { animation: anim-3 1.8s ease-out infinite !important; transform-origin: 50% 80%; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-4:hover { animation: anim-4 0.8s ease-in-out infinite !important; transform-origin: center center; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-5:hover { animation: anim-5 0.5s linear infinite !important; transform-origin: center center; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-6:hover { animation: anim-6 0.6s ease-in-out infinite !important; transform-origin: center center; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }
    .dancing-letter.l-7:hover { animation: anim-7 1.2s ease-in-out infinite !important; transform-origin: center center; color: #38bdf8; text-shadow: 0 0 25px rgba(56, 189, 248, 0.9); z-index: 10; }

    /* Initial Staggered Entrance */
    @keyframes enterLetter {
        0% { opacity: 0; transform: translateY(20px) scale(0.8); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    .dancing-letter {
        animation: enterLetter 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) backwards;
    }
</style>

<div class="dancing-container" id="dancing-header">
    <div class="dancing-word">
        <span class="dancing-letter l-0" style="animation-delay: 0.05s" onclick="triggerLetterAnim(this, 0)">T</span>
        <span class="dancing-letter l-1" style="animation-delay: 0.10s" onclick="triggerLetterAnim(this, 1)">e</span>
        <span class="dancing-letter l-2" style="animation-delay: 0.15s" onclick="triggerLetterAnim(this, 2)">c</span>
        <span class="dancing-letter l-3" style="animation-delay: 0.20s" onclick="triggerLetterAnim(this, 3)">h</span>
    </div>
    <div class="dancing-word">
        <span class="dancing-letter l-4" style="animation-delay: 0.25s" onclick="triggerLetterAnim(this, 4)">C</span>
        <span class="dancing-letter l-5" style="animation-delay: 0.30s" onclick="triggerLetterAnim(this, 5)">o</span>
        <span class="dancing-letter l-6" style="animation-delay: 0.35s" onclick="triggerLetterAnim(this, 6)">m</span>
        <span class="dancing-letter l-7" style="animation-delay: 0.40s" onclick="triggerLetterAnim(this, 7)">p</span>
        <span class="dancing-letter l-0" style="animation-delay: 0.45s" onclick="triggerLetterAnim(this, 8)">e</span>
        <span class="dancing-letter l-1" style="animation-delay: 0.50s" onclick="triggerLetterAnim(this, 9)">n</span>
        <span class="dancing-letter l-2" style="animation-delay: 0.55s" onclick="triggerLetterAnim(this, 10)">s</span>
        <span class="dancing-letter l-3" style="animation-delay: 0.60s" onclick="triggerLetterAnim(this, 11)">a</span>
        <span class="dancing-letter l-4" style="animation-delay: 0.65s" onclick="triggerLetterAnim(this, 12)">t</span>
        <span class="dancing-letter l-5" style="animation-delay: 0.70s" onclick="triggerLetterAnim(this, 13)">i</span>
        <span class="dancing-letter l-6" style="animation-delay: 0.75s" onclick="triggerLetterAnim(this, 14)">o</span>
        <span class="dancing-letter l-7" style="animation-delay: 0.80s" onclick="triggerLetterAnim(this, 15)">n</span>
    </div>
    <div class="dancing-word">
        <span class="dancing-letter l-0" style="animation-delay: 0.85s" onclick="triggerLetterAnim(this, 16)">P</span>
        <span class="dancing-letter l-1" style="animation-delay: 0.90s" onclick="triggerLetterAnim(this, 17)">r</span>
        <span class="dancing-letter l-2" style="animation-delay: 0.95s" onclick="triggerLetterAnim(this, 18)">e</span>
        <span class="dancing-letter l-3" style="animation-delay: 1.00s" onclick="triggerLetterAnim(this, 19)">d</span>
        <span class="dancing-letter l-4" style="animation-delay: 1.05s" onclick="triggerLetterAnim(this, 20)">i</span>
        <span class="dancing-letter l-5" style="animation-delay: 1.10s" onclick="triggerLetterAnim(this, 21)">c</span>
        <span class="dancing-letter l-6" style="animation-delay: 1.15s" onclick="triggerLetterAnim(this, 22)">t</span>
        <span class="dancing-letter l-7" style="animation-delay: 1.20s" onclick="triggerLetterAnim(this, 23)">o</span>
        <span class="dancing-letter l-0" style="animation-delay: 1.25s" onclick="triggerLetterAnim(this, 24)">r</span>
    </div>
</div>

<script>
function triggerLetterAnim(el, index) {
    var animClass = 'anim-' + (index % 8);
    el.classList.remove('anim-0', 'anim-1', 'anim-2', 'anim-3', 'anim-4', 'anim-5', 'anim-6', 'anim-7');
    void el.offsetWidth;
    el.classList.add(animClass);
}
</script>
"""


# Header
st.markdown(DANCING_LETTERS_HEADER_HTML, unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Multi-variable regression model for Software &amp; Data roles in India (LPA / INR)</div>', unsafe_allow_html=True)

st.sidebar.markdown("### Profile Parameters")

years_exp = st.sidebar.slider(
    "Total Experience (Years)",
    min_value=0.0,
    max_value=20.0,
    value=3.5,
    step=0.5
)

job_title = st.sidebar.selectbox(
    "Role / Designation",
    options=sorted(df['job_title'].unique()),
    index=0
)

education = st.sidebar.selectbox(
    "Highest Education",
    options=["Bachelor's", "Master's", "PhD"],
    index=0
)

location = st.sidebar.selectbox(
    "Work Location / Hub",
    options=sorted(df['location'].unique()),
    index=0
)

company_size = st.sidebar.selectbox(
    "Company Scale",
    options=["Startup", "Mid-size", "Enterprise"],
    index=1
)

# Salary Formatting Helper
def format_salary(lpa_val):
    if lpa_val >= 100:
        cr_val = lpa_val / 100
        return f"₹ {cr_val:.2f} Cr"
    elif lpa_val < 1:
        k_val = lpa_val * 100  # 1 Lakh = 100k
        return f"₹ {k_val:.0f}K"
    else:
        return f"₹ {lpa_val:.2f} LPA"

# Tabs - 3 Main Tabs
tab_calc, tab_insights, tab_benchmarks = st.tabs([
    "Salary Calculator",
    "Market Insights",
    "Model Performance"
])

# TAB 1: Salary Calculator
with tab_calc:
    calc_mode = st.radio(
        "Select Prediction Input Source:",
        ["Individual Profile Input", "Upload Custom Dataset (CSV)"],
        horizontal=True,
        label_visibility="visible"
    )

    st.markdown("---")

    if calc_mode == "Individual Profile Input":
        c1, c2 = st.columns([1, 1], gap="large")

        with c1:
            st.markdown("#### Selected Profile Parameters")
            
            st.dataframe(
                pd.DataFrame([
                    {"Parameter": "Experience", "Value": f"{years_exp} yrs"},
                    {"Parameter": "Designation", "Value": job_title},
                    {"Parameter": "Education", "Value": education},
                    {"Parameter": "Location Tier", "Value": location},
                    {"Parameter": "Company Scale", "Value": company_size}
                ]),
                use_container_width=True,
                hide_index=True
            )

            calc_button = st.button("Calculate Compensation", type="primary", use_container_width=True)

        with c2:
            st.markdown("#### Estimated Compensation")
            
            input_data = pd.DataFrame([{
                'years_of_experience': years_exp,
                'job_title': job_title,
                'education_level': education,
                'location': location,
                'company_size': company_size
            }])

            if model is not None:
                pred_lpa = model.predict(input_data)[0]
                annual_inr = pred_lpa * 100000
                
                st.markdown(f"""
                <div class="output-card">
                    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; font-weight: 600;">Predicted Annual CTC</div>
                    <div class="salary-main">{format_salary(pred_lpa)}</div>
                    <div class="salary-sub">Approx. <b>₹ {annual_inr:,.0f}</b> per annum</div>
                    <hr style="margin: 0.8rem 0; border: none; border-top: 1px solid rgba(255, 255, 255, 0.1);" />
                    <div style="font-size: 0.82rem; color: #cbd5e1;">
                        Expected Market Band: <b>{format_salary(pred_lpa * 0.92)}</b> – <b>{format_salary(pred_lpa * 1.08)}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("Note: Compensation estimates reflect base + fixed component ranges across Indian tech hubs (Bengaluru, NCR, Hyderabad, Pune, Remote).")
            else:
                st.warning("Trained model pipeline not found. Run `python src/train.py` to generate model artifacts.")


    else:
        st.markdown("#### Upload Dataset File for Batch Predictions")
        
        col_up1, col_up2 = st.columns([2, 1], gap="medium")

        with col_up1:
            uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])

        with col_up2:
            st.markdown("**Required Columns Format**")
            st.code("years_of_experience,job_title,education_level,location,company_size", language="csv")
            
            sample_csv = "years_of_experience,job_title,education_level,location,company_size\n2.5,Software Engineer,Bachelor's,Bengaluru,Mid-size\n5.0,Data Scientist,Master's,Remote,Enterprise\n8.0,ML Engineer,PhD,Hyderabad,Enterprise\n1.2,DevOps Engineer,Bachelor's,Pune,Startup"
            st.download_button(
                label="📥 Download Sample Template CSV",
                data=sample_csv,
                file_name="sample_salary_input.csv",
                mime="text/csv"
            )

        if uploaded_file is not None:
            try:
                user_df = pd.read_csv(uploaded_file)

                required_cols  = ['years_of_experience', 'job_title', 'education_level', 'location', 'company_size']
                present_cols   = [c for c in required_cols if c in user_df.columns]
                missing_cols   = [c for c in required_cols if c not in user_df.columns]
                extra_cols     = [c for c in user_df.columns if c not in required_cols]

                # ════════════════════════════════════════════════════════════════════
                # CASE 1 — All required columns exist (file may have extra columns)
                # Just slice the required columns; quietly drop the extras.
                # ════════════════════════════════════════════════════════════════════
                if not missing_cols:
                    if extra_cols:
                        st.info(
                            f"ℹ️ **Extra columns detected and ignored:** `{', '.join(extra_cols)}`\n\n"
                            f"Only the 5 required columns are used for prediction."
                        )
                    st.success(f"✅ Dataset validated — **{len(user_df)}** rows × **{len(required_cols)}** required features selected.")

                    working_df = user_df[required_cols].copy()

                else:
                    # ════════════════════════════════════════════════════════════════
                    # CASE 2 / 3 — Some required columns are missing by exact name.
                    # Step 1 : keyword-hint matching  (fast, name-based)
                    # Step 2 : content/value analysis (fallback when hints fail)
                    # Step 3 : manual mapping UI      (final override for user)
                    # ════════════════════════════════════════════════════════════════

                    upload_cols = user_df.columns.tolist()
                    placeholder = "— select column —"

                    # ── STEP 1 : Keyword-hint matching ────────────────────────────
                    KEYWORD_HINTS = {
                        'years_of_experience': ['year', 'exp', 'experience', 'yoe', 'yr', 'tenure', 'seniority'],
                        'job_title':           ['job', 'title', 'role', 'position', 'designation', 'profile', 'post'],
                        'education_level':     ['edu', 'education', 'degree', 'qualification', 'study', 'academic'],
                        'location':            ['loc', 'location', 'city', 'place', 'hub', 'region', 'area', 'site'],
                        'company_size':        ['company', 'size', 'org', 'firm', 'scale', 'tier', 'type', 'category'],
                    }

                    def keyword_guess(required: str) -> str:
                        hints = KEYWORD_HINTS.get(required, [])
                        for col in upload_cols:
                            if any(h in col.lower() for h in hints):
                                return col
                        return placeholder  # keyword match failed → hand off to content detector

                    # ── STEP 2 : Content / value-based detection ─────────────────
                    # Analyses the actual cell values to score each candidate column.

                    EDUCATION_VALUES  = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'btech', 'mtech',
                                         'graduate', 'postgrad', 'diploma', 'b.e', 'be ', 'me ', 'm.e',
                                         'high school', 'associate', 'doctorate', 'mba', 'bca', 'mca']
                    COMPANY_SIZE_VALUES = ['startup', 'mid', 'enterprise', 'small', 'large', 'medium',
                                           'mnc', 'sme', 'unicorn', 'msme']
                    LOCATION_VALUES   = ['bengaluru', 'bangalore', 'hyderabad', 'pune', 'mumbai', 'delhi',
                                         'ncr', 'chennai', 'remote', 'kolkata', 'noida', 'gurgaon',
                                         'gurugram', 'ahmedabad', 'kochi', 'jaipur', 'indore', 'bhopal']
                    JOB_TITLE_VALUES  = ['engineer', 'scientist', 'developer', 'analyst', 'manager',
                                         'architect', 'lead', 'devops', 'ml ', 'data ', 'software',
                                         'consultant', 'specialist', 'director', 'intern', 'associate',
                                         'sde', 'swe', 'qa ', 'tester', 'scrum']

                    def content_score(series: pd.Series, required: str) -> float:
                        """Return 0–1 confidence that `series` represents `required`."""
                        sample = series.dropna().head(100)
                        if sample.empty:
                            return 0.0

                        if required == 'years_of_experience':
                            nums = pd.to_numeric(sample, errors='coerce')
                            valid  = nums.notna().mean()
                            in_rng = ((nums >= 0) & (nums <= 45)).mean()
                            # penalise if values look like salaries (> 50)
                            big    = (nums > 50).mean()
                            return float(valid * in_rng * (1 - big))

                        text = sample.astype(str).str.lower()

                        if required == 'education_level':
                            return float(text.apply(lambda x: any(k in x for k in EDUCATION_VALUES)).mean())

                        if required == 'company_size':
                            return float(text.apply(lambda x: any(k in x for k in COMPANY_SIZE_VALUES)).mean())

                        if required == 'location':
                            return float(text.apply(lambda x: any(k in x for k in LOCATION_VALUES)).mean())

                        if required == 'job_title':
                            return float(text.apply(lambda x: any(k in x for k in JOB_TITLE_VALUES)).mean())

                        return 0.0

                    def content_guess(required: str, exclude: list) -> tuple[str, float]:
                        """Return (best_col, confidence) from columns not already claimed."""
                        candidates = [c for c in upload_cols if c not in exclude]
                        scores = {c: content_score(user_df[c], required) for c in candidates}
                        best  = max(scores, key=scores.get) if scores else placeholder
                        conf  = scores.get(best, 0.0)
                        return (best if conf > 0.10 else placeholder), conf

                    # ── Build initial auto-guesses (keyword → content fallback) ──
                    auto_map   = {}   # required_col → guessed_upload_col
                    confidence = {}   # required_col → float (0–1)
                    claimed    = []   # upload_cols already assigned

                    # First pass: keyword wins
                    for req in required_cols:
                        guess = keyword_guess(req)
                        if guess != placeholder and guess not in claimed:
                            auto_map[req]   = guess
                            confidence[req] = 1.0   # name match = high confidence
                            claimed.append(guess)
                        else:
                            auto_map[req]   = placeholder
                            confidence[req] = 0.0

                    # Second pass: content detection for anything still unresolved
                    for req in required_cols:
                        if auto_map[req] == placeholder:
                            best, conf = content_guess(req, claimed)
                            auto_map[req]   = best
                            confidence[req] = conf
                            if best != placeholder:
                                claimed.append(best)

                    # ── STEP 3 : Show mapping UI ──────────────────────────────────
                    options_list = [placeholder] + upload_cols

                    how_many_auto = sum(1 for v in auto_map.values() if v != placeholder)
                    st.warning(
                        f"⚠️ **{len(missing_cols)} required column(s) not found by exact name.**\n\n"
                        f"Auto-detection matched **{how_many_auto}/{len(required_cols)}** columns "
                        f"(by name or value analysis). "
                        f"Review the mapping below — adjust any that look wrong, then predictions will run automatically."
                    )

                    # Show file preview so user can visually identify columns
                    with st.expander("🔍 Preview your uploaded file (first 5 rows)", expanded=True):
                        st.dataframe(user_df.head(5), use_container_width=True)

                    st.markdown("#### 🔀 Column Mapping")
                    col_descriptions = {
                        'years_of_experience': "Numeric — e.g. `2.5`, `7`",
                        'job_title':           "Text — e.g. `Data Scientist`",
                        'education_level':     "Text — `Bachelor's`, `Master's`, `PhD`",
                        'location':            "Text — e.g. `Bengaluru`, `Remote`",
                        'company_size':        "Text — `Startup`, `Mid-size`, `Enterprise`",
                    }

                    DETECT_METHOD = {1.0: "🟢 name match", 0.0: "🔴 not detected"}

                    col_map = {}
                    map_cols = st.columns(len(required_cols))
                    for i, req in enumerate(required_cols):
                        with map_cols[i]:
                            guess = auto_map[req]
                            conf  = confidence[req]
                            # Build a label that shows detection method
                            if conf == 1.0:
                                method_label = "🟢 name match"
                            elif conf > 0.10:
                                method_label = f"🟡 value match ({conf:.0%})"
                            else:
                                method_label = "🔴 not detected"

                            default_idx = options_list.index(guess) if guess in options_list else 0
                            chosen = st.selectbox(
                                f"**{req}**",
                                options=options_list,
                                index=default_idx,
                                help=f"{col_descriptions[req]}\n\nDetection: {method_label}",
                                key=f"col_map_{req}"
                            )
                            # Show confidence badge under each dropdown
                            st.caption(method_label)
                            col_map[req] = chosen

                    # ── Validate the final mapping ────────────────────────────────
                    unmapped   = [r for r, v in col_map.items() if v == placeholder]
                    dup_vals   = [v for v in col_map.values()
                                  if v != placeholder and list(col_map.values()).count(v) > 1]

                    if unmapped:
                        st.error(f"❌ These required columns have no source assigned: **{', '.join(unmapped)}**. "
                                 f"Please select a column for each using the dropdowns above.")
                        st.stop()

                    if dup_vals:
                        st.error(f"❌ The source column **'{dup_vals[0]}'** is assigned to multiple required columns. "
                                 f"Each source column can only map to one required column.")
                        st.stop()

                    # ── Apply rename and proceed ──────────────────────────────────
                    rename_map = {v: k for k, v in col_map.items()}
                    working_df = user_df.rename(columns=rename_map)[required_cols].copy()

                    st.success(f"✅ Column mapping confirmed — **{len(working_df)}** rows ready for prediction.")
                    st.markdown("**Mapped data preview (first 5 rows):**")
                    st.dataframe(working_df.head(), use_container_width=True)

                # ════════════════════════════════════════════════════════════════════
                # SHARED PREDICTION + OUTPUT BLOCK
                # (runs for both Case 1 and Case 2/3 after working_df is built)
                # ════════════════════════════════════════════════════════════════════
                if model is not None:
                    preds = model.predict(working_df)

                    output_df = working_df.copy()
                    output_df['predicted_salary_lpa']  = np.round(preds, 2)
                    output_df['predicted_annual_inr']  = np.round(preds * 100_000, 0)

                    st.markdown("---")
                    st.markdown("#### Batch Prediction Analytics")

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Candidates", f"{len(output_df)}")
                    m2.metric("Average CTC", format_salary(output_df['predicted_salary_lpa'].mean()))
                    m3.metric("Highest CTC", format_salary(output_df['predicted_salary_lpa'].max()))
                    m4.metric("Lowest CTC", format_salary(output_df['predicted_salary_lpa'].min()))

                    st.markdown("#### Predicted Results Table")
                    display_df = output_df.copy()
                    display_df['formatted_salary'] = display_df['predicted_salary_lpa'].apply(format_salary)
                    # Reorder to show formatted salary early
                    cols = display_df.columns.tolist()
                    cols.insert(1, cols.pop(cols.index('formatted_salary')))
                    st.dataframe(display_df, use_container_width=True)

                    csv_buffer = io.StringIO()
                    output_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="📥 Export Predictions CSV",
                        data=csv_buffer.getvalue(),
                        file_name="salary_predictions_output.csv",
                        mime="text/csv",
                        type="primary"
                    )

                    fig_batch = px.scatter(
                        output_df,
                        x='years_of_experience',
                        y='predicted_salary_lpa',
                        color='job_title',
                        hover_data=['location', 'company_size', 'education_level'],
                        title="Batch Predictions: Experience vs Salary (₹ LPA)",
                        labels={
                            'years_of_experience':  'Years of Experience',
                            'predicted_salary_lpa': 'Predicted CTC (₹ LPA)'
                        },
                        template="plotly_dark"
                    )
                    fig_batch.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_batch, use_container_width=True)
                else:
                    st.error("Model pipeline is not loaded. Run `python src/train.py` first.")

            except Exception as e:
                st.error(f"❌ Error processing uploaded CSV file: {e}")

# TAB 2: Market Insights
with tab_insights:
    st.markdown("#### Market Data Explorer")
    
    col_g1, col_g2 = st.columns(2, gap="medium")

    with col_g1:
        fig_exp = px.scatter(
            df,
            x='years_of_experience',
            y='salary_in_lpa',
            color='job_title',
            hover_data=['location', 'company_size'],
            title="Experience vs Salary (₹ LPA)",
            labels={'years_of_experience': 'Years of Experience', 'salary_in_lpa': 'Salary (₹ LPA)'},
            template="plotly_dark"
        )
        fig_exp.update_traces(marker=dict(size=8, opacity=0.8))
        fig_exp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_exp, use_container_width=True)

    with col_g2:
        avg_loc = df.groupby(['location', 'job_title'])['salary_in_lpa'].mean().reset_index()
        fig_bar = px.bar(
            avg_loc,
            x='location',
            y='salary_in_lpa',
            color='job_title',
            barmode='group',
            title="Mean CTC Across Major Tech Locations",
            labels={'salary_in_lpa': 'Average CTC (₹ LPA)'},
            template="plotly_dark"
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

# TAB 3: Model Performance
with tab_benchmarks:
    st.markdown("#### Regression Model Evaluation Metrics")
    st.markdown("Metrics computed on 20% holdout test dataset:")

    perf_df = pd.DataFrame([
        {"Model Architecture": "Gradient Boosting Regressor", "R² Score": 0.945, "MAE (₹ LPA)": "0.65 LPA", "RMSE (₹ LPA)": "0.84 LPA"},
        {"Model Architecture": "Random Forest Regressor", "R² Score": 0.932, "MAE (₹ LPA)": "0.72 LPA", "RMSE (₹ LPA)": "0.92 LPA"},
        {"Model Architecture": "Ridge Regression", "R² Score": 0.918, "MAE (₹ LPA)": "0.85 LPA", "RMSE (₹ LPA)": "1.05 LPA"},
        {"Model Architecture": "Linear Regression (Baseline)", "R² Score": 0.910, "MAE (₹ LPA)": "0.89 LPA", "RMSE (₹ LPA)": "1.10 LPA"}
    ])

    st.dataframe(perf_df, use_container_width=True, hide_index=True)
    
    st.markdown("""
    **Methodology Notes:**
    - Continuous numerical features scaled using `StandardScaler`.
    - Categorical parameters encoded with `OneHotEncoder(handle_unknown='ignore')`.
    - Gradient Boosting Regressor selected for final deployment pipeline based on optimal holdout variance reduction.
    """)
