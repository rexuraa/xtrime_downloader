import os
import shutil
import subprocess
import requests
from rich.console import Console

console = Console()

LOGO_PATH = "/sdcard/DCIM/Xtrime/rexuraa.png"
SAVE_DIR_VIDEO = "/sdcard/Download/XTRIME"
SAVE_DIR_MUSIC = "/sdcard/Download/XTRIME/Music"
serial_file_video = "/data/data/com.termux/files/home/.xtrime_serial.txt"
serial_file_music = "/data/data/com.termux/files/home/.xtrime_music_serial.txt"

def download_logo():
    logo_url = "https://raw.githubusercontent.com/rexuraa/rexuraa_logo/main/rexuraa.png"
    save_path = LOGO_PATH
    if not os.path.exists("/sdcard/DCIM/Xtrime"):
        os.makedirs("/sdcard/DCIM/Xtrime")
    if not os.path.exists(save_path):
        console.print("[cyan]🌐 Downloading logo from GitHub...[/]")
        try:
            response = requests.get(logo_url)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                console.print("[green]✅ Logo downloaded![/]")
            else:
                console.print("[red]❌ Failed to download logo![/]")
        except Exception as e:
            console.print(f"[red]❌ Error downloading logo:[/] {e}")

def banner():
    os.system("clear")
    console.print("\n[bold cyan]🌀 XTRIME MULTIMEDIA DOWNLOADER 🌀[/]", justify="center")
    console.print("[bold green]Max Quality • Watermark • MP3 • By REXURAA[/]\n", justify="center")

def get_next_serial(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("1")
        return 1
    with open(path, "r") as f:
        return int(f.read())

def update_serial(path, serial):
    with open(path, "w") as f:
        f.write(str(serial + 1))

def download_video(url, raw_name, is_youtube=False):
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
            ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", "-o", raw_name, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        subprocess.run(
            ["yt-dlp", "-f", "bv*+ba/b", "-o", raw_name, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    console.print("[bold green]✅ Download complete![/]")

def apply_watermark(input_video, output_video):
    console.print("[bold blue]🎬 Adding Watermark...[/]")
    cmd = (
        f'ffmpeg -y -i "{input_video}" -i "{LOGO_PATH}" '
        f'-filter_complex "[1:v]scale=215:-1[wm];[0:v][wm]overlay=(W-w)/2:H-h-18" '
        f'-preset ultrafast -c:v libx264 -crf 20 -c:a copy "{output_video}" > /dev/null 2>&1'
    )
    
    os.system(cmd)
    console.print("[bold green]✅ Watermark added successfully![/]")
    
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def move_to_gallery(output_video):
    if not os.path.exists(SAVE_DIR_VIDEO):
        os.makedirs(SAVE_DIR_VIDEO)
    final_path = os.path.join(SAVE_DIR_VIDEO, os.path.basename(output_video))
    shutil.move(output_video, final_path)
    os.system(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}')
    console.print(f"[bold green]✅ Saved to Gallery:[/] {final_path}")

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
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final_path = os.path.join(SAVE_DIR_MUSIC, output_name)
    os.system(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}')
    console.print(f"[bold green]🎧 Saved MP3 to:[/] {final_path}")

def video_mode():
    while True:
        banner()
        url = input("🔗 Enter Video URL (or press Enter to go back): ").strip()
        if not url:
            break

        yt_check = input("Is this a YouTube URL? (y/n): ").strip().lower()
        is_youtube = (yt_check == 'y')

        serial = get_next_serial(serial_file_video)
        raw_name = "temp_video.mp4"
        final_name = f"Xtrime Video No.{serial}.mp4"

        for f in [raw_name, final_name]:
            if os.path.exists(f):
                os.remove(f)

        download_video(url, raw_name, is_youtube)

        if not os.path.exists(raw_name):
            console.print("[red]❌ Download failed! Check your link or connection.[/]")
            continue

        apply_watermark(raw_name, final_name)
        move_to_gallery(final_name)
        update_serial(serial_file_video, serial)

        again = input("\n🔁 Download another video? (y/n): ").strip().lower()
        if again != 'y':
            break

def music_mode():
    while True:
        banner()
        url = input("🔗 Enter Music/Video URL (or press Enter to go back): ").strip()
        if not url:
            break

        console.print("\n[bold cyan]🎧 Choose Audio Quality:[/]")
        console.print("1. 320kbps (Best)\n2. 128kbps (Standard)")
        choice = input("Select (1/2): ").strip()
        quality = "0" if choice == "1" else "5"

        serial = get_next_serial(serial_file_music)
        filename = f"Xtrime Music No.{serial}.mp3"

        download_music(url, filename, quality)
        update_serial(serial_file_music, serial)

        again = input("\n🔁 Download another song? (y/n): ").strip().lower()
        if again != 'y':
            break

def main():
    download_logo()
    while True:
        banner()
        console.print("🔘 [bold white]Select Mode:[/]")
        console.print("1. 🎥 Video Download\n2. 🎵 Music Download (MP3)\n3. ❌ Exit\n")
        mode = input("Enter choice (1/2/3): ").strip()
        if mode == "1":
            video_mode()
        elif mode == "2":
            music_mode()
        elif mode == "3":
            console.print("[bold cyan]👋 Exiting XTRIME Downloader. Bye![/]")
            break
        else:
            console.print("[red]❌ Invalid choice! Try again.[/]")

if __name__ == "__main__":
    main()
