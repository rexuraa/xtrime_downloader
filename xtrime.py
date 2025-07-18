import os
import shutil
import subprocess
import requests
import re
import json
import socket
import time
from datetime import datetime
from rich.console import Console
from rich.progress import Progress

console = Console()

# Configuration
LOGO_PATH = "/sdcard/DCIM/Xtrime/rexuraa.png"
SAVE_DIR_VIDEO = "/sdcard/XTRIME MULTIMEDIA/Videos"
SAVE_DIR_MUSIC = "/sdcard/XTRIME MULTIMEDIA/Music"
SAVE_DIR_IMAGE = "/sdcard/XTRIME MULTIMEDIA/Images"
serial_file_video = "/data/data/com.termux/files/home/.xtrime_serial.txt"
serial_file_music = "/data/data/com.termux/files/home/.xtrime_music_serial.txt"
serial_file_image = "/data/data/com.termux/files/home/.xtrime_image_serial.txt"
HISTORY_FILE = "/data/data/com.termux/files/home/.xtrime_history.json"
TEMP_DIR = "/data/data/com.termux/files/home/temp_xtrime"

# Utility Functions
def silent_run(cmd, shell=False):
    subprocess.run(cmd, shell=shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def try_command(cmd, success_msg=None, fail_msg=None, shell=False):
    try:
        result = subprocess.run(cmd, shell=shell, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if result.returncode != 0:
            if fail_msg:
                console.print(f"[red]{fail_msg}[/]")
                console.print(result.stderr.decode())
            return False
        if success_msg:
            console.print(f"[green]{success_msg}[/]")
        return True
    except Exception as e:
        console.print(f"[red]Command failed: {e}[/]")
        return False

def has_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def is_valid_url(url):
    pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'(www\.)?'  # www.
        r'([a-zA-Z0-9_\-]+\.)+'  # domain and subdomains
        r'[a-zA-Z]{2,}'  # TLD
        r'(/[\w\-./?%&=]*)?$'  # path and query parameters
    )
    return re.match(pattern, url) is not None

def input_choice(prompt, options):
    while True:
        choice = input(prompt).strip().lower()
        if choice in options:
            return choice
        console.print("[red]Invalid input, try again![/]")

def banner():
    os.system("clear")
    console.print("\n[bold cyan]🌀 XTRIME MULTIMEDIA DOWNLOADER 🌀[/]", justify="center")
    console.print("[bold green]Max Quality • Watermark • MP3 • By REXURAA[/]\n", justify="center")

def get_next_serial(path):
    try:
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("1")
            return 1
        with open(path, "r") as f:
            return int(f.read().strip())
    except:
        return 1

def update_serial(path, serial):
    with open(path, "w") as f:
        f.write(str(serial + 1))

def get_file_size(path):
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def save_to_history(file_type, file_path):
    try:
        history = load_history()
        history.append({
            "type": file_type,
            "path": file_path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "size": get_file_size(file_path)
        })
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        console.print(f"[red]Error saving history: {e}[/]")

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        return []
    except:
        return []

def show_history():
    history = load_history()
    console.print("\n[bold cyan]📜 DOWNLOAD HISTORY[/]")
    if not history:
        console.print("[yellow]No downloads yet![/]")
    else:
        for idx, item in enumerate(reversed(history), 1):
            console.print(f"{idx}. [bold]{item['type'].upper()}[/] - {item['date']}")
            console.print(f"   [dim]{item['path']} ({item.get('size', 'N/A')}[/]")

def cleanup_temp_files():
    try:
        temp_files = [f for f in os.listdir(TEMP_DIR) if f.startswith(("temp_", "cut_")) and f.endswith((".mp4", ".mp3", ".jpg"))]
        for file in temp_files:
            os.remove(os.path.join(TEMP_DIR, file))
        console.print(f"[green]Cleaned {len(temp_files)} temp files![/]")
    except Exception as e:
        console.print(f"[red]Error cleaning temp files: {e}[/]")

def clear_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            f.write("[]")
        console.print("[green]History cleared![/]")
    except Exception as e:
        console.print(f"[red]Error clearing history: {e}[/]")

def download_logo():
    try:
        logo_dir = os.path.dirname(LOGO_PATH)
        if not os.path.exists(logo_dir):
            os.makedirs(logo_dir)

        if not os.path.exists(LOGO_PATH):
            console.print("[cyan]Downloading logo...[/]")
            url = "https://raw.githubusercontent.com/rexuraa/rexuraa_logo/main/rexuraa.png"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(LOGO_PATH, "wb") as f:
                    f.write(r.content)
                console.print("[green]Logo downloaded![/]")
            else:
                console.print(f"[red]Failed to download logo: HTTP {r.status_code}[/]")
    except Exception as e:
        console.print(f"[red]Logo download error: {e}[/]")

def get_video_duration(input_path):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0
    except:
        return 0

def move_to_gallery(file_path, file_type="video"):
    try:
        if file_type == "video":
            save_dir = SAVE_DIR_VIDEO
        elif file_type == "music":
            save_dir = SAVE_DIR_MUSIC
        elif file_type == "image":
            save_dir = SAVE_DIR_IMAGE
        else:
            save_dir = SAVE_DIR_VIDEO

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        final_path = os.path.join(save_dir, os.path.basename(file_path))
        
        # Handle duplicate filenames
        counter = 1
        name, ext = os.path.splitext(final_path)
        while os.path.exists(final_path):
            final_path = f"{name}_{counter}{ext}"
            counter += 1

        shutil.move(file_path, final_path)
        
        # Update media scanner
        silent_run(['am', 'broadcast', '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE', '-d', f'file://{final_path}'])
        
        console.print(f"[green]Saved: {final_path} ({get_file_size(final_path)})[/]")
        return final_path
        
    except Exception as e:
        console.print(f"[red]Error moving file: {e}[/]")
        return None

def apply_blur_effect_with_progress(input_path, output_path, aspect="square", with_logo=True):
    try:
        duration = get_video_duration(input_path)
        if duration <= 0:
            console.print("[red]Could not get video duration[/]")
            return False

        # Prepare logo filter if needed
        logo_filter = ""
        logo_input = []
        if with_logo and os.path.exists(LOGO_PATH):
            logo_filter = "[1:v]scale=180:-1[logo];[final][logo]overlay=W-w-10:H-h-400[outv]"
            logo_input = ["-i", LOGO_PATH]
        else:
            logo_filter = "[final]copy[outv]"

        # Prepare scaling based on aspect
        if aspect == "square":
            scale_filter = "scale=1080:1080:force_original_aspect_ratio=decrease,crop=1080:1080"
        else:
            scale_filter = "scale=1080:-2"

        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,boxblur=20[bg];"
            f"[0:v]{scale_filter}[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[final];"
            f"{logo_filter}"
        )

        cmd = [
            'ffmpeg', '-y', '-hide_banner',
            '-i', input_path,
            *logo_input,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '20',
            '-c:a', 'copy',
            '-movflags', '+faststart',
            output_path
        ]

        start_time = time.time()
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing video...", total=duration)
            
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )

            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                    
                # Parse time for progress
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match:
                    hours, minutes, seconds = time_match.groups()
                    current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    progress.update(task, completed=current_time)

                # Print any error messages
                if 'error' in line.lower():
                    console.print(f"[red]FFmpeg Error: {line.strip()}[/]")

        if process.returncode != 0:
            console.print("[red]Video processing failed![/]")
            return False

        console.print("[green]Blur effect applied successfully![/]")
        return True

    except Exception as e:
        console.print(f"[red]Error during processing: {str(e)}[/]")
        return False

def apply_padding_with_logo(input_path, output_path, pad_color, add_logo=True):
    try:
        # Validate and normalize color
        if not pad_color.startswith('#') and pad_color.lower() not in [
            'black', 'white', 'red', 'green', 'blue', 'yellow', 
            'orange', 'purple', 'pink', 'navy', 'teal', 'olive', 
            'maroon', 'gold', 'brown', 'skyblue', 'indigo', 
            'cyan', 'magenta', 'lime'
        ]:
            pad_color = '#' + pad_color.lstrip('#')
        
        duration = get_video_duration(input_path)
        if duration <= 0:
            console.print("[red]Could not get video duration[/]")
            return False

        # Build filter complex based on logo requirement
        if add_logo and os.path.exists(LOGO_PATH):
            filter_complex = (
                f"[0:v]scale=1080:-2:force_original_aspect_ratio=decrease,"
                f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:{pad_color},setsar=1[padded];"
                f"[1:v]scale=180:-1[logo];"
                f"[padded][logo]overlay=W-w-10:H-h-400"
            )
            cmd = [
                "ffmpeg", "-y", "-hide_banner",
                "-i", input_path,
                "-i", LOGO_PATH,
                "-filter_complex", filter_complex,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "20",
                "-c:a", "copy",
                "-movflags", "+faststart",
                output_path
            ]
        else:
            filter_complex = (
                f"[0:v]scale=1080:-2:force_original_aspect_ratio=decrease,"
                f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:{pad_color},setsar=1"
            )
            cmd = [
                "ffmpeg", "-y", "-hide_banner",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "20",
                "-c:a", "copy",
                "-movflags", "+faststart",
                output_path
            ]

        # Execute with progress
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Processing...", total=duration)
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                    
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match:
                    h, m, s = time_match.groups()
                    current_sec = int(h)*3600 + int(m)*60 + float(s)
                    progress.update(task, completed=current_sec)

        if process.returncode != 0:
            console.print("[red]Processing failed[/]")
            return False

        console.print(f"[green]Successfully processed![/]")
        return True

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        return False

def rotate_video(input_path, output_path, rotation, add_logo=True):
    try:
        duration = get_video_duration(input_path)
        if duration <= 0:
            console.print("[red]Could not get video duration[/]")
            return False

        logo_filter = ""
        logo_input = []
        if add_logo and os.path.exists(LOGO_PATH):
            logo_filter = "[1:v]scale=180:-1[logo];[rotated][logo]overlay=W-w-15:H-h-20[outv]"
            logo_input = ["-i", LOGO_PATH]
        else:
            logo_filter = "[rotated]copy[outv]"

        if rotation == "90":
            rotate_filter = "transpose=1"
        elif rotation == "180":
            rotate_filter = "transpose=1,transpose=1"
        elif rotation == "270":
            rotate_filter = "transpose=2"
        else:
            rotate_filter = "hflip"
        
        filter_complex = (
            f"[0:v]{rotate_filter}[rotated];"
            f"{logo_filter}"
        )

        cmd = [
            'ffmpeg', '-y', '-hide_banner',
            '-i', input_path,
            *logo_input,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '20', 
            '-c:a', 'copy', 
            '-movflags', '+faststart',
            output_path
        ]

        with Progress() as progress:
            task = progress.add_task("[cyan]Rotating video...", total=duration)
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if 'time=' in line:
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                    if time_match:
                        h, m, s = time_match.groups()
                        current_time = float(h)*3600 + float(m)*60 + float(s)
                        progress.update(task, completed=current_time)

        if process.returncode != 0:
            console.print("[red]Video rotation failed![/]")
            return False

        console.print("[green]✅ Video rotated successfully![/]")
        return True

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        return False
        
def rooted_video_mode():
    while True:
        banner()
        console.print("\n[bold cyan]🔄 ROOTED VIDEO TOOL[/]")
        console.print("1. From Device Storage")
        console.print("2. Download Online")
        console.print("3. ↩️ Back to Advanced Menu")
        
        choice = input_choice("Select (1-3): ", ["1", "2", "3"])
        if choice == "3":
            break

        input_path = os.path.join(TEMP_DIR, "temp_rooted.mp4")

        if choice == "1":
            if not check_storage_permission():
                continue
            video_name = input("\nEnter video filename (e.g. video.mp4): ").strip()
            if not video_name:
                continue
            video_path = find_video_file(video_name)
            if not video_path:
                continue
            try:
                shutil.copy2(video_path, input_path)
                console.print(f"[green]✓ Video loaded![/]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")
                continue

        elif choice == "2":
            url = input("\nEnter URL: ").strip()
            if not url:
                continue
            if not download_video(url, input_path, is_youtube=False):
                continue

        console.print("\n🔄 [bold]Select Rotation:[/]")
        console.print("1. Rotate 90° Clockwise")
        console.print("2. Rotate 180°")
        console.print("3. Rotate 270° Clockwise")
        console.print("4. Flip Horizontal")
        rotation = input_choice("Choose (1-4): ", ["1", "2", "3", "4"])
        rotation = {"1": "90", "2": "180", "3": "270", "4": "hflip"}[rotation]

        add_logo = input_choice("\nAdd logo? (y/n): ", ["y", "n"]) == 'y'

        serial = get_next_serial(serial_file_video)
        output_path = os.path.join(TEMP_DIR, f"Xtrime Rooted {serial}.mp4")

        if rotate_video(input_path, output_path, rotation, add_logo):
            saved_path = move_to_gallery(output_path)
            if saved_path:
                save_to_history("video", saved_path)
                update_serial(serial_file_video, serial)

        for f in [input_path, output_path]:
            if os.path.exists(f):
                os.remove(f)

        if input("\nProcess another? (y/n): ").lower() != 'y':
            break

def apply_watermark(raw_path, watermarked_path):
    console.print("[bold blue]🎬 Adding Watermark...[/]")
    cmd = (
        f'ffmpeg -y -i "{raw_path}" -i "{LOGO_PATH}" '
        f'-filter_complex "[1:v]scale=180:-1[wm];[0:v][wm]overlay=W-w-10:H-h-25" '
        f'-preset ultrafast -c:v libx264 -crf 20 -c:a copy "{watermarked_path}"'
    )
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    console.print("[bold green]✅ Watermark added successfully![/]")
    return True

def download_video(url, raw_path, is_youtube=False):
    console.print(f"[bold yellow]📥 Downloading:[/] {url}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "filesize_approx", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best", url],
            capture_output=True, text=True
        )
        size_bytes = result.stdout.strip()
        size_mb = round(int(size_bytes) / (1024 * 1024), 2)
        console.print(f"[bold magenta]📦 Estimated size:[/] {size_mb} MB")
    except:
        console.print("[italic yellow]⚠️ Could not detect file size.[/]")

    if is_youtube:
        subprocess.run(
            ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", "-o", raw_path, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        subprocess.run(
            ["yt-dlp", "-f", "bv*+ba/b", "-o", raw_path, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    console.print("[bold green]✅ Download complete![/]")
    return True 

def download_music(url, output_name, quality):
    if not os.path.exists(SAVE_DIR_MUSIC):
        os.makedirs(SAVE_DIR_MUSIC)
    console.print(f"[bold yellow]🎵 Downloading music:[/] {url}")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", quality,
        "-o", os.path.join(SAVE_DIR_MUSIC, output_name),
        url
    ]
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading...", total=100)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
                
            if output:
                # Parse download progress
                download_match = re.search(r'(\d+\.\d+)%', output)
                if download_match:
                    progress.update(task, completed=float(download_match.group(1)))

    final_path = os.path.join(SAVE_DIR_MUSIC, output_name)
    os.system(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}')
    console.print(f"[bold green]🎧 Saved MP3 to:[/] {final_path}")
    return final_path

def video_mode():
    while True:
        banner()
        console.print("\n[bold cyan]🎥 VIDEO DOWNLOADER[/]")
        url = input("Enter video URL (or press Enter to go back): ").strip()
        if not url:
            break

        if not is_valid_url(url):
            console.print("[red]Invalid URL provided![/]")
            time.sleep(2)
            continue

        is_youtube = input_choice("Is this YouTube? (y/n): ", ["y", "n"]) == 'y'

        serial = get_next_serial(serial_file_video)
        raw_name = f"temp_video_{serial}.mp4"
        final_name = f"Xtrime Video {serial}.mp4"
        
        raw_path = os.path.join(TEMP_DIR, raw_name)
        watermarked_path = os.path.join(TEMP_DIR, final_name)

        # Download video
        if not download_video(url, raw_path, is_youtube):
            input("Press Enter to continue...")
            continue

        # Ask for watermark
        add_watermark = input_choice("\nAdd watermark? (y/n): ", ["y", "n"]) == 'y'

        if add_watermark:
            if not os.path.exists(LOGO_PATH):
                console.print("[red]Logo not found! Proceeding without watermark.[/]")
                add_watermark = False

        if add_watermark:
            if not apply_watermark(raw_path, watermarked_path):
                console.print("[yellow]Proceeding without watermark[/]")
                shutil.copy(raw_path, watermarked_path)
        else:
            shutil.copy(raw_path, watermarked_path)

        # Move to gallery
        saved_path = move_to_gallery(watermarked_path)
        if saved_path:
            save_to_history("video", saved_path)
            update_serial(serial_file_video, serial)

        # Cleanup
        for f in [raw_path, watermarked_path]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

        if input("\nDownload another? (y/n): ").strip().lower() != 'y':
            break

def music_mode():
    while True:
        banner()
        console.print("\n[bold cyan]🎵 AUDIO DOWNLOADER[/]")
        url = input("Enter audio URL (or press Enter to go back): ").strip()
        if not url:
            break

        if not is_valid_url(url):
            console.print("[red]Invalid URL provided![/]")
            time.sleep(2)
            continue

        quality = input_choice("\nSelect quality:\n1. Best (320K)\n2. High (192K)\n3. Medium (128K)\n> ", ["1", "2", "3"])
        quality_map = {"1": "320K", "2": "192K", "3": "128K"}
        selected_quality = quality_map[quality]

        serial = get_next_serial(serial_file_music)
        final_name = f"Xtrime Music {serial}.mp3"

        # Download music
        saved_path = download_music(url, final_name, selected_quality)
        if saved_path:
            save_to_history("music", saved_path)
            update_serial(serial_file_music, serial)

        if input("\nDownload another? (y/n): ").strip().lower() != 'y':
            break

def video_cut_mode():
    while True:
        banner()
        console.print("\n[bold cyan]✂️ VIDEO CUTTER[/]")
        
        console.print("\n[cyan]📁 Select Source:[/]")
        console.print("1. From Device Storage")
        console.print("2. Download Online")
        source = input_choice("Choose (1/2): ", ["1", "2"])

        input_path = None
        output_path = None

        if source == "1":
            if not check_storage_permission():
                continue

            video_name = input("\nEnter video filename (e.g. video.mp4): ").strip()
            if not video_name:
                continue

            video_path = find_video_file(video_name)
            if not video_path:
                continue

            input_path = os.path.join(TEMP_DIR, f"temp_cut_{os.path.basename(video_path)}")
            try:
                shutil.copy2(video_path, input_path)
                console.print(f"[green]✓ Ready: {video_path}[/]")
            except Exception as e:
                console.print(f"[red]Copy failed: {e}[/]")
                continue

        elif source == "2":
            url = input("\nEnter URL: ").strip()
            if not url:
                continue

            is_youtube = input_choice("Is this YouTube? (y/n): ", ["y", "n"]) == 'y'
            input_path = os.path.join(TEMP_DIR, "temp_cut.mp4")

            if not download_video(url, input_path, is_youtube):
                continue

        # ===== COMMON VIDEO CUTTING SECTION FOR BOTH =====
        duration = get_video_duration(input_path)
        if duration <= 0:
            console.print("[red]Could not get video duration[/]")
            if os.path.exists(input_path):
                os.remove(input_path)
            continue

        console.print(f"\nVideo duration: {time.strftime('%H:%M:%S', time.gmtime(duration))}")
        
        # Start Time
        console.print("\nEnter start time (e.g. 1:30 or 90s or 1m30s):")
        start_time = input("Leave empty to start from beginning: ").strip()

        # End Time
        console.print("\nEnter end time (e.g. 2:00 or 120s or 2m):")
        end_time = input(f"Leave empty to go to end (max {time.strftime('%H:%M:%S', time.gmtime(duration))}): ").strip()

        # Parse times
        def parse_time(t):
            try:
                if ':' in t:
                    parts = list(map(float, t.split(':')))
                    if len(parts) == 2:
                        return parts[0]*60 + parts[1]
                    elif len(parts) == 3:
                        return parts[0]*3600 + parts[1]*60 + parts[2]
                elif 'h' in t or 'm' in t or 's' in t:
                    sec = 0
                    if 'h' in t:
                        sec += int(t.split('h')[0]) * 3600
                        t = t.split('h')[1]
                    if 'm' in t:
                        sec += int(t.split('m')[0]) * 60
                        t = t.split('m')[1]
                    if 's' in t:
                        sec += int(t.split('s')[0])
                    return sec
                else:
                    return float(t)
            except:
                return None

        start_sec = parse_time(start_time) if start_time else 0
        end_sec = parse_time(end_time) if end_time else duration

        if start_sec is None:
            console.print("[red]Invalid start time! Using 0[/]")
            start_sec = 0
        if end_sec is None:
            console.print(f"[red]Invalid end time! Using full duration ({duration}s)[/]")
            end_sec = duration

        if start_sec >= end_sec:
            console.print("[red]Start time must be before end time![/]")
            if os.path.exists(input_path):
                os.remove(input_path)
            continue

        if end_sec > duration:
            console.print("[yellow]End time exceeds video duration, using max duration[/]")
            end_sec = duration

        # Prepare output
        serial = get_next_serial(serial_file_video)
        output_name = f"Xtrime Cut {serial}.mp4"
        output_path = os.path.join(TEMP_DIR, output_name)

        console.print(f"\nCutting from {time.strftime('%H:%M:%S', time.gmtime(start_sec))} to {time.strftime('%H:%M:%S', time.gmtime(end_sec))}")
        start_time_str = time.strftime('%H:%M:%S', time.gmtime(start_sec))
        end_time_str = time.strftime('%H:%M:%S', time.gmtime(end_sec))

        if not cut_video(input_path, output_path, start_time_str, end_time_str):
            if os.path.exists(input_path):
                os.remove(input_path)
            continue

        # Ask for watermark
        add_watermark = input_choice("\nAdd watermark? (y/n): ", ["y", "n"]) == 'y'
        if add_watermark and os.path.exists(LOGO_PATH):
            watermarked_path = os.path.join(TEMP_DIR, f"watermarked_{output_name}")
            if apply_watermark(output_path, watermarked_path):
                os.remove(output_path)
                output_path = watermarked_path
            else:
                console.print("[yellow]Proceeding without watermark[/]")

        # Move to gallery
        saved_path = move_to_gallery(output_path)
        if saved_path:
            save_to_history("video", saved_path)
            update_serial(serial_file_video, serial)

        # Cleanup
        for f in [input_path, output_path]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

        if input("\nCut another? (y/n): ").strip().lower() != 'y':
            break

def advance_video_mode():
    while True:
        banner()
        console.print("\n[bold cyan]🚀 ENHANCED ADVANCED MODE[/]")
        console.print("1. Blur BG + Center Video (With Progress)")
        console.print("2. Add Color Bar/Pad (With Progress)")
        console.print("3. Rotate/Flip Video (Rooted Tool)")
        console.print("4. ↩️ Back to Main Menu")

        choice = input_choice("Select (1-4): ", ["1", "2", "3", "4"])
        if choice == "4":
            break

        console.print("\n[cyan]📁 Select Source:[/]")
        console.print("1. From Device Storage")
        console.print("2. Download Online")
        source = input_choice("Choose (1/2): ", ["1", "2"])

        input_path = None
        os.makedirs(TEMP_DIR, exist_ok=True)

        if source == "1":
            if not check_storage_permission():
                continue

            video_name = input("\nEnter video filename (e.g. video.mp4): ").strip()
            if not video_name:
                continue

            video_path = find_video_file(video_name)
            if not video_path:
                continue

            input_path = os.path.join(TEMP_DIR, f"temp_adv_{os.path.basename(video_path)}")
            try:
                with Progress() as progress:
                    task = progress.add_task(f"[cyan]Copying {video_name}...", total=100)
                    shutil.copy2(video_path, input_path)
                    progress.update(task, completed=100)
                console.print(f"[green]✓ Ready: {video_path}[/]")
            except Exception as e:
                console.print(f"[red]Copy failed: {e}[/]")
                continue

        elif source == "2":
            url = input("\nEnter URL: ").strip()
            if not url:
                continue

            is_youtube = input_choice("Is this YouTube? (y/n): ", ["y", "n"]) == 'y'
            input_path = os.path.join(TEMP_DIR, "temp_adv.mp4")

            if not download_video(url, input_path, is_youtube):
                continue

        serial = get_next_serial(serial_file_video)
        final_name = f"Xtrime Adv {serial}.mp4"
        output_path = os.path.join(TEMP_DIR, final_name)
        
        if choice == "1":
            mode = input_choice("\n[cyan]Choose mode:\n1. Square (1:1)\n2. Original Aspect\n> ", ["1", "2"])
            aspect = "square" if mode == "1" else "original"
            add_logo = input_choice("\nAdd logo? (y/n): ", ["y", "n"]) == 'y'

            if not apply_blur_effect_with_progress(input_path, output_path, aspect, add_logo):
                continue

            saved_path = move_to_gallery(output_path)
            if saved_path:
                save_to_history("video", saved_path)
                console.print("[green]✓ Blur effect applied![/]")
                
        elif choice == "2":
            console.print("\n🎨 [bold cyan]Select a padding color:[/]\n")
            color_options = [
                ("🔲 Black", "black"),
                ("⬜ White", "white"),
                ("🌫 Dark Gray", "#222222"),
                ("🌁 Light Gray", "#CCCCCC"),
                ("🔴 Red", "red"),
                ("🟢 Green", "green"),
                ("🔵 Blue", "blue"),
                ("🟡 Yellow", "yellow"),
                ("🟠 Orange", "orange"),
                ("🟣 Purple", "purple"),
                ("🌸 Pink", "pink"),
                ("⚓ Navy", "navy"),
                ("🧿 Teal", "teal"),
                ("🌿 Olive", "olive"),
                ("🍷 Maroon", "maroon"),
                ("🏅 Gold", "gold"),
                ("🪵 Brown", "brown"),
                ("☁️ Sky Blue", "skyblue"),
                ("🥴 Indigo", "indigo"),
                ("🌀 Cyan", "cyan"),
                ("💖 Magenta", "magenta"),
                ("🍏 Lime", "lime"),
                ("🎨 Custom Color", "custom")
            ]

            for i, (emoji_text, hex_code) in enumerate(color_options, 1):
                console.print(f"{i:2d}. {emoji_text:<20}")

            selection = input("\nEnter your choice (1-23): ").strip()

            try:
                selected_index = int(selection) - 1
                if 0 <= selected_index < len(color_options)-1:
                    selected_color = color_options[selected_index][1]
                elif selected_index == len(color_options)-1:
                    selected_color = input("\nEnter custom color hex/code (e.g. #123456 or red): ").strip()
                else:
                    console.print("[red]Invalid selection! Using default (black)[/]")
                    selected_color = "black"
            except ValueError:
                console.print("[red]Invalid input! Using default (black)[/]")
                selected_color = "black"

            add_logo = input_choice("\nAdd logo? (y/n): ", ["y", "n"]) == 'y'
            
            if not apply_padding_with_logo(input_path, output_path, selected_color, add_logo):
                continue

            saved_path = move_to_gallery(output_path)
            if saved_path:
                save_to_history("video", saved_path)
                console.print(f"[green]✓ Padded with {selected_color} {'+ logo' if add_logo else ''}![/]")

        elif choice == "3":  # New Rooted Video Option
            console.print("\n🔄 [bold cyan]Select Rotation:[/]")
            console.print("1. Rotate 90° Clockwise")
            console.print("2. Rotate 180°")
            console.print("3. Rotate 270° Clockwise")
            console.print("4. Flip Horizontal")
            rotation_choice = input_choice("Select (1-4): ", ["1", "2", "3", "4"])
            rotation = {"1": "90", "2": "180", "3": "270", "4": "hflip"}[rotation_choice]

            add_logo = input_choice("\nAdd logo? (y/n): ", ["y", "n"]) == 'y'

            if not rotate_video(input_path, output_path, rotation, add_logo):
                continue

            saved_path = move_to_gallery(output_path)
            if saved_path:
                save_to_history("video", saved_path)
                console.print("[bold]✓ Video rotated successfully![/]")

        # Clean up
        for f in [input_path, output_path]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

        if input("\nProcess another? (y/n): ").strip().lower() != 'y':
            break

def image_downloader_mode():
    while True:
        banner()
        console.print("\n[bold cyan]📷 IMAGE DOWNLOADER[/]")
        
        url = input("Enter image URL (or press Enter to exit): ").strip()
        if not url:
            break

        if not is_valid_url(url):
            console.print("[red]Invalid URL provided![/]")
            continue

        serial = get_next_serial(serial_file_image)
        filename = f"Xtrime Image {serial}.jpg"
        output_path = os.path.join(TEMP_DIR, filename)
        final_path = os.path.join(SAVE_DIR_IMAGE, filename)

        try:
            console.print("[yellow]Downloading image...[/]")
            
            with Progress() as progress:
                task = progress.add_task("[cyan]Downloading...", total=100)
                
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress.update(task, completed=(downloaded / total_size) * 100)
                            else:
                                progress.update(task, advance=1)
            
            # Move to final location
            shutil.move(output_path, final_path)
            
            # Update media scanner
            silent_run(['am', 'broadcast', '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE', '-d', f'file://{final_path}'])
            
            file_size = get_file_size(final_path)
            console.print(f"[green]Image saved: {final_path} (Size: {file_size})[/]")
            
            save_to_history("image", final_path)
            update_serial(serial_file_image, serial)
            
        except Exception as e:
            console.print(f"[red]Image Download Error: {e}[/]")
            if os.path.exists(output_path):
                os.remove(output_path)
        
        if input("\nDownload another? (y/n): ").strip().lower() != 'y':
            break

def history_menu():
    while True:
        banner()
        show_history()

        console.print("\n1. 🗑️ Delete Temporary Files")
        console.print("2. 📝 Clear History")
        console.print("3. ↩️ Back to Main Menu")

        choice = input_choice("Select: ", ["1", "2", "3"])

        if choice == "1":
            cleanup_temp_files()
            input("Press Enter to continue...")
        elif choice == "2":
            clear_history()
            input("Press Enter to continue...")
        elif choice == "3":
            break

def check_storage_permission():
    if not os.path.exists(os.path.expanduser("~/storage/shared")):
        console.print("[red]Storage permission not granted![/]")
        console.print("[yellow]Please run: termux-setup-storage[/]")
        return False
    return True

def find_video_file(filename):
    search_locations = [
        os.path.expanduser("~/storage/shared/DCIM"),
        os.path.expanduser("~/storage/shared/Download"),
        os.path.expanduser("~/storage/shared/Movies"),
        os.path.expanduser("~/storage/shared/Videos")
    ]
    
    found_files = []
    for location in search_locations:
        if os.path.exists(location):
            for root, _, files in os.walk(location):
                if filename in files:
                    found_files.append(os.path.join(root, filename))
    
    if not found_files:
        console.print(f"[red]File '{filename}' not found![/]")
        return None
    
    if len(found_files) == 1:
        return found_files[0]
    
    console.print("[yellow]Multiple files found:[/]")
    for i, file_path in enumerate(found_files, 1):
        console.print(f"{i}. {file_path}")
    
    try:
        selection = int(input("Select file number: ")) - 1
        if 0 <= selection < len(found_files):
            return found_files[selection]
    except ValueError:
        pass
    
    console.print("[red]Invalid selection![/]")
    return None

def cut_video(input_path, output_path, start_time=None, end_time=None):
    try:
        duration = get_video_duration(input_path)
        if duration <= 0:
            console.print("[red]Could not get video duration[/]")
            return False

        cut_cmd = ['ffmpeg', '-y', '-loglevel', 'error']
        if start_time:
            cut_cmd += ['-ss', start_time]
        if end_time:
            cut_cmd += ['-to', end_time]
        cut_cmd += ['-i', input_path, '-c', 'copy', '-movflags', '+faststart', output_path]

        with Progress() as progress:
            task = progress.add_task("[cyan]Cutting video...", total=duration)
            
            process = subprocess.Popen(
                cut_cmd,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', output)
                    if match:
                        h, m, s = match.groups()
                        current_time = float(h)*3600 + float(m)*60 + float(s)
                        progress.update(task, completed=current_time)
            
            if process.returncode != 0:
                console.print(f"[red]Video cutting failed![/]")
                return False
        
        console.print("[green]Video cut completed![/]")
        return True
    except Exception as e:
        console.print(f"[red]Error during cutting: {str(e)}[/]")
        return False

def main():
    # Create necessary directories
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(SAVE_DIR_VIDEO, exist_ok=True)
    os.makedirs(SAVE_DIR_MUSIC, exist_ok=True)
    os.makedirs(SAVE_DIR_IMAGE, exist_ok=True)
    
    download_logo()
    
    while True:
        banner()
        console.print("🔘 [bold]MAIN MENU[/]")
        console.print("1. 🎥 Video Downloader")
        console.print("2. 🎵 Audio Downloader")
        console.print("3. ✂️ Video Cutter")
        console.print("4. 🚀 Advanced Tools")
        console.print("5. 📜 View History/Cleanup")
        console.print("6. 📷 Image Downloader")
        console.print("7. ❌ Exit")

        choice = input_choice("Select (1-7): ", ["1","2","3","4","5","6","7"])

        if choice == "1":
            video_mode()
        elif choice == "2":
            music_mode()
        elif choice == "3":
            video_cut_mode()
        elif choice == "4":
            advance_video_mode()
        elif choice == "5":
            history_menu()
        elif choice == "6":
            image_downloader_mode()
        elif choice == "7":
            console.print("[bold cyan]👋 Exiting XTRIME Downloader.  Bye..![/]")
            cleanup_temp_files()
            break

if __name__ == "__main__":
    main()
