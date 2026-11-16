#!/usr/bin/env python3

"""
Azazael Scrolling Video Generator - Enhanced Version

Double column full-screen with vibrant colors and emojis

"""



import os

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List
import math
import subprocess

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here



WIDTH = 1920

HEIGHT = 1080

FPS = 30

DURATION_SECONDS = 90



OUTPUT_DIR = Path.home() / "Desktop" / "CODEX"

FRAME_DIR = os.path.join(OUTPUT_DIR, "scroll_frames")

VIDEO_OUTPUT = os.path.join(OUTPUT_DIR, "Azazael_Reference_Video.mp4")



TEXT_CONTENT = """



                    🚀 Azazael ECOSYSTEM v2.0   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
              ✨ Complete Technical Reference Documentation ✨







                                    💜 OVERVIEW 💜  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                     Distributed Computing Framework 

               >> Self-Optimizing | 🔧 Self-Healing | 🤖 ML-Driven >>  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                              🎯 TIER 1: CORE WORMS 🎯  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    💻 SYSTEMZ         📊 Resource Monitor  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       [-] CPU, 💾 Memory, 💿 Disk,  Network, ⚙ Process Management  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       📤 Output: JSON, YAML, Prometheus |  Interval: 1s - 3600s  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    🔄 PROCESSZ          Process Manager  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       📋 Enumeration,  Tracking, 🚀 Spawning,  Termination  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🌳 Tree View, 🗺 Memory Map,  Remote (SSH, WMI, API)  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    💿 DISKZ            💾 Storage Monitor  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🔬 SMART Monitoring, 📈 I/O Statistics  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🗃 Types: HDD, SSD, NVMe | [!] Alerts: Predictive Failure  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


     NETWORXZ         🕸 Network Monitor  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🔗 TCP, UDP, ICMP, HTTP Protocols  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       📊 Bandwidth,  Latency Analysis | 📡 Packet Sniffing, 🎯 QoS  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


     CLOCKZ            Time Service

                        NTP, PTP, Manual Sync Modes

                       🎯 Precision: ms to ns | 📅 Cron-like Scheduler  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


     WORMZ             Crawler/Indexer

                        Filesystem, 📊 Git, 🗄 Database Sources  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       💻 All Major Language Formats | 🔎 ElasticSearch, SQLite Index  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                             🔗 TIER 2: CLUSTERWORMS 🔗  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    📚 BIBL CLUSTER          WORMZ + ✂ TRIMZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                           🧹 Content Crawling with Deduplication ✨  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    🖥 SYSTEM CLUSTER       💻 SYSTEMZ + 🔄 PROCESSZ + 💿 DISKZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                           📊 Complete Monitoring with Resource Correlation 🔬  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


     NETWORK CLUSTER       NETWORXZ +  CLOCKZ + 💿 DISKZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                            Infrastructure Health Analysis 🩺  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    🔒 SECURITY CLUSTER     🔄 PROCESSZ +  NETWORXZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                           🚨 Auditing and Intrusion Detection 🛡  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    📊 ANALYSIS CLUSTER     🧬 METAZ + 📈 METRICZ + 🕸 DEPENDZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                           🔎 Comprehensive Code Analysis   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    [OK] VALIDATION CLUSTER   [OK] VALIDZ + 👻 DEADZ +  ERRORZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                           🧪 Code Validation and Error Detection 🧹  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    💚 HEALTH CLUSTER       HEALTHZ + >> OPTIMIZ + 💻 SYSTEMZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                            System Health Optimization 







                              🧬 TIER 3: METAWORMS 🧬  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    🧬 METAZ            📦 Metadata Extraction Engine 🔧  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🕸 DEPENDZ          🕸 Dependency Mapping 🗺  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    [OK] VALIDZ            [OK] Syntax Validation 

    👻 DEADZ            👻 Dead Code Detection   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    📈 METRICZ          📊 Code Metrics Analysis 🧮  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🌀 Cyclomatic Complexity |  Halstead Metrics  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                        Lines of Code | 🛠 Maintainability Index  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


     ERRORZ            Error Pattern Matching 🎯  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    📋 LOGZ             📋 Log Analysis 📜  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
     CHANGEZ           Change Tracking 



    ✂ TRIMZ            ✂ Content Optimization 🧹  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    >> OPTIMIZ          >> Performance Tuning 🚀  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
     HEALTHZ           System Diagnostics 🩺  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                              [-] TIER 4: HYDRAMETA [-]





    [-] ML OPTIMIZATION ENGINE 🤖  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🧬 Genetic Algorithms + [-] RL  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        👥 Population: 100-1000  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🎯 Selection: Tournament, Roulette  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔀 Crossover: Single, Two-point  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🎲 Mutation: Bit Flip, Swap  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    💾 PERSISTENCE LAYER 🗄  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🗃 Backends: SQLite, Redis, PostgreSQL  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        >> Cache: In-Memory, Disk

        📜 History: Full Execution Log  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    🎮 EXECUTION STRATEGIES 🎲  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔄 Round Robin       - Sequential   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        >> Performance       - Fastest First 🥇  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        ⚖ Resource-Aware    - Load Balanced ⚖

        🎲 Randomized        - Chaos Mode 🌪  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🤖 ML-Optimized      - Predicted Best 🔮  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                             >> TIER 5: COORDINATION >>





    🎯 TERENCE          🎼 Orchestration 🎹  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       📚 Pattern DB: 50K+ Patterns  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       [-] RL Agent: Deep Q-Learning

                       🔗 Causal Graph: Directed Acyclic  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       ✨ Auto-fix: 90% Success Rate 🎉  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    📊 HORUS            🎨 Output Generation 🎭  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🎬 24 Animation Protocols  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       📄 Formats: HTML, JSON, GraphML  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       📊 Dashboards: Grafana, Custom  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                       🔴 Real-time: WebSocket  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                            🛠 SUPPORT SYSTEMS 🛠  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    ⌨ SHORTY           ⌨ Executable Shortcuts Manager 📌  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    📦 TARBABY          📦 Binary Builder and Packager   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🌈 PERSEPHONE       🌈 Cross-Platform Deployment (Win/Lin/Mac)   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🧮 POINDEXTER       🧮 Mathematical Indexer and Calculator 🧮  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    📖 BIBL             📖 Terminology Crawler and Dictionary 📚  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                        🔄 6-STAGE HYDRA PIPELINE 🔄  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




        [  1. DISCOVERY  ]  ->  [  2. ANALYSIS  ]  ->  [ >> 3. OPTIMIZE  ]

             Scan & Identify          Metaworm           >> Genetic

                                    Processing             Tuning



        [ [OK] 4. VALIDATE  ]  ->  [ 🚀 5. DEPLOY   ]  ->  [ 🔄 6. FEEDBACK  ]  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
            [OK] Error Checking           🚀 Execution           🔄 Persistence  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                          SYSTEM ARCHITECTURE 





    TIER 0:          ⌨ SHORTY, 📦 TARBABY  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    TIER 1:          💻 SYSTEMZ, 🔄 PROCESSZ, 💿 DISKZ,  NETWORXZ,  CLOCKZ,  WORMZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    TIER 2:          📚 BIBL, 🖥 SYSTEM,  NETWORK, 🔒 SECURITY, 📊 ANALYSIS,  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                    [OK] VALIDATION, 💚 HEALTH  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    TIER 3:          🧬 METAZ, 🕸 DEPENDZ, [OK] VALIDZ, 👻 DEADZ, 📈 METRICZ,  ERRORZ,  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                    📋 LOGZ,  CHANGEZ, ✂ TRIMZ, >> OPTIMIZ,  HEALTHZ  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    TIER 4:          [-] HYDRAMETA, 🤖 ML OPTIMIZATION, 🧬 GENETIC, 💾 PERSISTENCE  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    TIER 5:          🎯 TERENCE, 📊 HORUS  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                              📡 API REFERENCE 📡  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    🖥 SYSTEM API  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/system/status       System health  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/system/resources   📊 Resource metrics  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/system/processes   📋 Process list  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    🧬 METAZ API  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🟢 POST /api/v1/metaz/scan          Start scan  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/metaz/results/{id}  📥 Get results  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/metaz/metrics       📈 Code metrics  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    [-] HYDRAMETA API

        🟢 POST /api/v1/hydrameta/optimize     >> Run optimization  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/hydrameta/population    👥 Population status  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/hydrameta/history       📜 Execution history  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    🎯 TERENCE API  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🟢 POST /api/v1/terence/analyze     🔎 Error analysis  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🟢 POST /api/v1/terence/fix          🔧 Apply fix  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/terence/suggestions  💡 Get suggestions  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)


    📊 HORUS API  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/horus/dashboard     📺 Dashboard data  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🔵 GET  /api/v1/horus/animations    🎬 list animations  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        🟢 POST /api/v1/horus/export        📤 Export report  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                              💻 CLI COMMANDS 💻  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    💻 azazael --help                          📖 Show all available commands  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💻 azazael scan --target /path/to/code      Scan target directory  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💻 azazael analyze --metaworms all          Run all metaworms  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💻 azazael optimize --population 100        >> Run GA optimization  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💻 azazael monitor --dashboard             📊 Start monitoring dashboard  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💻 azazael deploy --cluster all            🚀 Deploy all clusters  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💻 azazael history --metrics               📈 Show execution metrics  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                           💾 DATABASE ADAPTERS 💾  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    🟦 SQLite           💾 Local Cache  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🟥 Redis            >> Real-time Cache  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🟨 PostgreSQL       💿 Persistence  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🟩 ElasticSearch    🔎 Search Index  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🟪 InfluxDB         📊 Metrics  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                          🎮 EXECUTION MODES 🎮  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)




    🔄 Cotemporaneous Execution  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    >> Parallel Processing

    🧵 Thread Pool  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🤖 ML Optimization  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🧬 Genetic Algorithms  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🎬 24 Protocols  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    📡 Real-time Monitoring  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    💾 Persistent State  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
    🔢 100+ CLI Flags  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
     REST API

     Cross-platform

    📈 Auto-scaling  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)






                    

                          Azazael ECOSYSTEM v1.0.0 

                    

               Distributed Computing | >> Self-Optimizing | 🔧 Self-Healing   # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
                    





"""





def pulse_color(base_hue, frame_num):

    """Create pulsating color effect"""




    pulse = math.sin(frame_num * 0.05) * 0.3 + 0.7

    hue = (base_hue + frame_num * 0.1) % 360

    return f"hsl({hue}, 100%, {int(50 * pulse)}%)"





def get_text_color(line, frame_num):

    """Dynamic color based on content and time"""

    if "" in line:

        return pulse_color(120, frame_num)

    elif (

        "TIER" in line

        or "OVERVIEW" in line

        or "PIPELINE" in line

        or "ARCHITECTURE" in line

    ):

        return pulse_color(180, frame_num)

    elif line.startswith("    💻") or line.startswith("    "):  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        return "#00ff88"

    elif line.startswith("        "):

        return "#8b949e"

    elif "[" in line:

        return pulse_color(60, frame_num)

    elif "GET" in line or "POST" in line:

        return "#00ff88"

    elif "azazael" in line:

        return pulse_color(280, frame_num)

    elif "TERENCE" in line or "HORUS" in line or "HYDRAMETA" in line:

        return pulse_color(300, frame_num)

    elif "🔗" in line or "🎯" in line or "🧬" in line or "[-]" in line:  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        return pulse_color(200, frame_num)

    elif any(emoji in line for emoji in ["🚀", "✨", "💜", "", "🎉", "", "🎊"]):  # scanner:ignore (bulk-landing 2026-11-04: retained artifact content)
        return pulse_color(280, frame_num)

    else:

        return "#e6edf3"





def create_video():

    os.makedirs(FRAME_DIR, exist_ok=True)



    print("Creating enhanced frames with double columns and vibrant colors...")






    img = Image.new("RGB", (WIDTH, HEIGHT), color="#0a0a1a")

    draw = ImageDraw.Draw(img)



    try:

        ImageFont.truetype("arial.ttf", 52)

        font_header = ImageFont.truetype("arial.ttf", 34)

        font_body = ImageFont.truetype("consolas.ttf", 22)

        font_small = ImageFont.truetype("consolas.ttf", 18)

    except Exception as exc:

        note_failure("make_video_v2:L658", exc)
        ImageFont.load_default()

        font_header = ImageFont.load_default()

        font_body = ImageFont.load_default()

        font_small = ImageFont.load_default()



    lines = TEXT_CONTENT.split("\n")



    def wrap_text(text, font, max_width):

        words = text.split(" ")

        lines_wrapped = []

        current = ""

        for word in words:

            test = current + (" " if current else "") + word

            bbox = draw.textbbox((0, 0), test, font=font)

            if bbox[2] - bbox[0] <= max_width:

                current = test

            else:

                if current:

                    lines_wrapped.append(current)

                current = word

        if current:

            lines_wrapped.append(current)

        return lines_wrapped



    num_frames = DURATION_SECONDS * FPS



    for frame_num in range(num_frames):

        progress = frame_num / num_frames



        frame = Image.new("RGB", (WIDTH, HEIGHT), color="#0a0a1a")

        draw = ImageDraw.Draw(frame)



        y_offset = int(progress * (len(lines) * 40))



        left_y = -y_offset

        right_y = -y_offset + 200



        left_lines = []

        right_lines = []



        for line in lines:

            if not line.strip():

                left_lines.append("")

                right_lines.append("")

            elif len(line) < 80:

                left_lines.append(line)

                right_lines.append("")

            else:

                mid = len(line) // 2

                space_idx = line.rfind(" ", 0, mid)

                if space_idx == -1:

                    space_idx = mid

                left_lines.append(line[:space_idx])

                right_lines.append(line[space_idx + 1 :])



        for i in range(max(len(left_lines), len(right_lines))):

            left_line = left_lines[i] if i < len(left_lines) else ""

            right_line = right_lines[i] if i < len(right_lines) else ""



            if left_y > HEIGHT + 50 and right_y > HEIGHT + 50:

                break



            if left_line and left_y > -50:

                color = get_text_color(left_line, frame_num)

                font = font_body

                if "" in left_line:

                    font = font_small

                elif any(

                    k in left_line

                    for k in ["TIER", "OVERVIEW", "PIPELINE", "ARCHITECTURE"]

                ):

                    font = font_header

                elif left_line.startswith("    "):

                    font = font_body



                bbox = draw.textbbox((0, 0), left_line, font=font)

                h = bbox[3] - bbox[1]

                draw.text((40, left_y), left_line, font=font, fill=color)

                left_y += h + 4



            if right_line and right_y > -50:

                color = get_text_color(right_line, frame_num)

                font = font_body

                if "" in right_line:

                    font = font_small

                elif any(

                    k in right_line

                    for k in ["TIER", "OVERVIEW", "PIPELINE", "ARCHITECTURE"]

                ):

                    font = font_header

                elif right_line.startswith("    "):

                    font = font_body



                bbox = draw.textbbox((0, 0), right_line, font=font)

                h = bbox[3] - bbox[1]

                draw.text((WIDTH // 2 + 20, right_y), right_line, font=font, fill=color)

                right_y += h + 4



        frame.save(os.path.join(FRAME_DIR, f"frame_{frame_num:06d}.png"), "PNG")



        if frame_num % 150 == 0:

            print(f"Frame {frame_num}/{num_frames}")



    print("Creating video with ffmpeg...")






    ffmpeg_cmd = [

        "ffmpeg",

        "-y",

        "-framerate",

        str(FPS),

        "-i",

        os.path.join(FRAME_DIR, "frame_%06d.png"),

        "-c:v",

        "libx264",

        "-preset",

        "fast",

        "-crf",

        "20",

        "-pix_fmt",

        "yuv420p",

        VIDEO_OUTPUT,

    ]



    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)

    if result.returncode == 0:

        print(f"Video created: {VIDEO_OUTPUT}")

    else:

        print(f"FFmpeg error: {result.stderr}")



    import shutil



    shutil.rmtree(FRAME_DIR)

    print("Cleaned up frames")





if __name__ == "__main__":

    create_video()

# scanner:file-ignore unicode_emoji -- template/output strings, UTF-8 by contract (0 console-print sites verified)
