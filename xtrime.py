import os
import shutil
import subprocess
import urllib.request
from rich.console import Console

console = Console()

LOGO_URL = "https://raw.githubusercontent.com/rexuraa/rexuraa_logo/main/rexuraa.png"
LOGO_PATH = "/sdcard/DCIM/Xtrime/rexuraa.png"
SAVE_DIR = "/sdcard/Download/XTRIME"
serial_file = "/data/data/com.termux/files/home/.xtrime_serial.txt"

def banner():
    os.system("clear")
    console.print("\n[bold cyan]🌀 XTRIME VIDEO DOWNLOADER 🌀[/]", justify="center")
    console.print("[bold green]Max Quality • Watermark • Serial Name • Gallery Save[/]\n", justify="center")

def download_logo():
    if not os.path.exists(LOGO_PATH):
        os.makedirs(os.path.dirname(LOGO_PATH), exist_ok=True)
        console.print("[cyan]🌐 Downloading logo from GitHub...[/]")
        try:
            urllib.request.urlretrieve(LOGO_URL, LOGO_PATH)
            console.print("[green]✅ Logo downloaded and saved.[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed to download logo:[/] {e}")

def get_next_serial():
    if not os.path.exists(serial_file):
        with open(serial_file, "w") as f:
            f.write("1")
        return 1
    with open(serial_file, "r") as f:
        return int(f.read())

def update_serial(serial):
    with open(serial_file, "w") as f:
        f.write(str(serial + 1))

def download_video(url, raw_name):
    console.print(f"[bold yellow]📥 Downloading:[/] {url}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "filesize_approx", "-f", "bv*+ba/b", url],
            capture_output=True, text=True
        )
        size_bytes = result.stdout.strip()
        size_mb = round(int(size_bytes) / (1024 * 1024), 2)
        console.print(f"[bold magenta]📦 Estimated size:[/] {size_mb} MB")
    except:
        console.print("[italic yellow]⚠️ Could not detect file size.[/]")

    subprocess.run(
        [
            "yt-dlp", "-f", "bv*+ba/b",
            "--external-downloader", "aria2c",
            "--external-downloader-args", "-x 16 -k 1M",
            "-o", raw_name, url
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    console.print("[bold green]✅ Download complete![/]")

def apply_watermark(input_video, output_video):
    console.print("[bold blue]🎬 Adding Watermark...[/]")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-i", LOGO_PATH,
        "-filter_complex", "[1:v]scale=215:-1[wm];[0:v][wm]overlay=(W-w)/2:H-h-18",
        "-preset", "ultrafast",
        "-c:v", "libx264",
        "-crf", "20",
        "-c:a", "copy",
        output_video
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def move_to_gallery(output_video):
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    final_path = os.path.join(SAVE_DIR, os.path.basename(output_video))
    shutil.move(output_video, final_path)
    os.system(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}')
    console.print(f"[bold green]✅ Saved to Gallery:[/] {final_path}")

def main():
    download_logo()
    while True:
        banner()
        url = input("🔗 Enter Video URL: ").strip()
        if not url:
            break

        serial = get_next_serial()
        raw_name = "temp_video.mp4"
        final_name = f"Xtrime Video No.{serial}.mp4"

        for f in [raw_name, final_name]:
            if os.path.exists(f):
                os.remove(f)

        download_video(url, raw_name)

        if not os.path.exists(raw_name):
            console.print("[red]❌ Download failed! Check your link or connection.[/]")
            continue

        apply_watermark(raw_name, final_name)
        move_to_gallery(final_name)
        update_serial(serial)

        again = input("\n🔁 Download another video? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main()
