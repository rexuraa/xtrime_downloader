import os
import shutil
import subprocess
import requests
import re
from rich.console import Console

console = Console()

LOGO_PATH = "/sdcard/DCIM/Xtrime/rexuraa.png"
SAVE_DIR_VIDEO = "/sdcard/Download/XTRIME"
SAVE_DIR_MUSIC = "/sdcard/Download/XTRIME/Music"
serial_file_video = "/data/data/com.termux/files/home/.xtrime_serial.txt"
serial_file_music = "/data/data/com.termux/files/home/.xtrime_music_serial.txt"


def download_logo():
    if not os.path.exists("/sdcard/DCIM/Xtrime"):
        os.makedirs("/sdcard/DCIM/Xtrime")
    if not os.path.exists(LOGO_PATH):
        console.print("[cyan]🌐 Downloading logo from GitHub...[/]")
        try:
            url = "https://raw.githubusercontent.com/rexuraa/rexuraa_logo/main/rexuraa.png"
            r = requests.get(url)
            if r.status_code == 200:
                with open(LOGO_PATH, "wb") as f:
                    f.write(r.content)
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
        f'-filter_complex "[1:v]scale=210:-1[wm];[0:v][wm]overlay=W-w-20:H-h-20" '
        f'-preset ultrafast -c:v libx264 -crf 20 -c:a copy "{output_video}"'
    )
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    console.print("[bold green]✅ Watermark added successfully![/]")


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


def parse_user_time(text):
    h = m = s = 0
    text = text.lower()

    # যদি শুধু সংখ্যা হয়, ধরে নিচ্ছি সেটা সেকেন্ড
    if re.fullmatch(r"\d+", text.strip()):
        text += "s"

    match = re.findall(r'(\d+)\s*(h|hour|hours|min|minutes|m|s|sec|seconds)', text)

    for val, unit in match:
        val = int(val)
        if unit.startswith('h'):
            h = val
        elif unit.startswith('m'):
            m = val
        elif unit.startswith('s'):
            s = val

    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"


def cut_video(input_path, output_path, start_time=None, end_time=None):
    console.print(f"[blue]✂️ Cutting video from {start_time} to {end_time}...[/]")

    cmd = ['ffmpeg', '-y']
    if start_time:
        cmd += ['-ss', str(start_time)]
    if end_time:
        cmd += ['-to', str(end_time)]

    cmd += ['-i', input_path, '-c', 'copy', output_path]

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode == 0:
        console.print("[green]✅ Video cut successfully![/]")
        return True
    else:
        console.print("[red]❌ Video cutting failed![/]")
        return False


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


def video_cut_mode():
    while True:
        banner()
        console.print("\n[bold cyan]🌀 XTRIME CUTTING VIDEO DOWNLOADER 🌀[/]")
        url = input("🔗 Enter Video URL (or press Enter to go back): ").strip()
        if not url:
            break

        yt_check = input("Is this a YouTube URL? (y/n): ").strip().lower()
        is_youtube = (yt_check == 'y')

        serial = get_next_serial(serial_file_video)
        raw_name = "temp_video.mp4"
        final_name = f"Xtrime Cut Video No.{serial}.mp4"

        for f in [raw_name, final_name, "cut_video.mp4"]:
            if os.path.exists(f):
                os.remove(f)

        download_video(url, raw_name, is_youtube)

        if not os.path.exists(raw_name):
            console.print("[red]❌ Download failed! Check your link or connection.[/]")
            continue

        console.print("\n[bold cyan]⏱️ Enter your desired cut range:[/]")
        start_input = input("🔹 Start from (e.g. 0s, 1min, 2min 10s): ").strip()
        end_input = input("🔸 End at (e.g. 26s, 1min 10s, 1h 5min): ").strip()

        start_time = parse_user_time(start_input)
        end_time = parse_user_time(end_input)

        cut_video_path = "cut_video.mp4"
        if cut_video(raw_name, cut_video_path, start_time, end_time):
            apply_watermark(cut_video_path, final_name)
            move_to_gallery(final_name)
        else:
            console.print("[red]⚠️ Cut failed. Using full video.[/]")
            apply_watermark(raw_name, final_name)
            move_to_gallery(final_name)

        update_serial(serial_file_video, serial)

        again = input("\n🔁 Download and cut another video? (y/n): ").strip().lower()
        if again != 'y':
            break


def main():
    download_logo()
    while True:
        banner()
        console.print("🔘 [bold white]Select Mode:[/]")
        console.print("1. 🎥 Full Video Downloader")
        console.print("2. 🎵 Music Downloader (MP3)")
        console.print("3. ✂️ Cutting Video Downloader")
        console.print("4. ❌ Exit\n")
        mode = input("Enter choice (1/2/3/4): ").strip()

        if mode == "1":
            video_mode()
        elif mode == "2":
            music_mode()
        elif mode == "3":
            video_cut_mode()
        elif mode == "4":
            console.print("[bold cyan]👋 Exiting XTRIME Downloader. Bye![/]")
            break
        else:
            console.print("[red]❌ Invalid choice! Try again.[/]")


if __name__ == "__main__":
    main()
