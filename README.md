<p align="center">
  <img src="https://raw.githubusercontent.com/rexuraa/rexuraa_logo/main/rexuraa.png" width="120" height="120" alt="Rexuraa Logo"/>
  <h4 align="center">🌀 XTRIME DOWNLOADER 🌀</h4>
  <p align="center"><strong>High-Quality •Auto Watermark •Serial Naming•All-in-One-Multimedia Tool</strong></p>
</p>

---

## 🚀 Features

✔ **Smart Downloading**  
- YouTube, Facebook, Instagram and 1000+ sites support  
- Best available quality (4K/1080p/720p auto-detection)  
- Background download support  

✔ **Automatic Processing**  
- Auto-numbering (Xtrime Video No.1, No.2...)  
- Watermark positioning (Bottom-right by default)  
- Gallery integration (Auto-appears in Photos app)  

✔ **Advanced Options**  
- Custom logo support  
- Multiple output formats (MP4, MP3, JPG)  
- Batch download capability  

---

## 📥 Installation Guide

```bash
pkg update && pkg upgrade -y
```
```
pkg install python ffmpeg aria2 git -y
```
```
pip install rich yt-dlp
```
```
termux-setup-storage
```
```
git clone https://github.com/rexuraa/xtrime_downloader.git
```
```
cd xtrime_downloader
```
```
pip install requests
```
---
### First Run
```bash
python xtrime.py
```
```
echo "cd ~/xtrime && python xtrime.py" >> ~/.bashrc  
source ~/.bashrc
```
```
xtrime
```
---

## 🖼️ Customization

### Changing Logo
1. Place your `logo.png` in:
   ```
   /sdcard/DCIM/Xtrime/rexuraa.png
   ```
2. Recommended size: 200x200px transparent PNG

### Output Locations
- Videos: `/sdcard/XTRIME MULTIMEDIA/Videos`
- Music: `/sdcard/XTRIME MULTIMEDIA/Music` 
- Images: `/sdcard/XTRIME MULTIMEDIA/Images`

---

## 🎯 Quick Start Guide

1. **Run the tool**:
   ```bash
   python xtrime.py
   ```
```
   echo "cd ~/xtrime && python xtrime.py" >> ~/.bashrc  
source ~/.bashrc
```
```
xtrime
```
3. **Main Menu**:
   ```
   1. 🎥 Video Downloader
   2. 🎵 Audio Downloader
   3. ✂️ Video Cutter
   4. 🚀 Advanced Tools
   5. 📷 Image Downloader
   ```

4. **Example Flow**:
   ```
   🔗 Enter Video URL :https://youtu.be/example
   📦 Estimated size: 125MB (1080p)
   ⏳ Downloading...
   🎬 Processing watermark...
   ✅ Saved: Xtrime Video No.15.mp4
   ```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Download fails | Run `yt-dlp --update` |
| Watermark not appearing | Check logo exists at `/sdcard/DCIM/Xtrime/` |
| Videos not in Gallery | Run `termux-setup-storage` again |

---

## 🌟 Advanced Features

### Video Editing Tools
- Background blur effect
- Color padding (black bars)
- Precise video trimming (HH:MM:SS)

### Audio Extraction
- Convert videos to MP3
- Quality selection (128kbps to 320kbps)

---

## 📜 Version History
`v1.0` - Initial release (Basic downloading)  
`v1.5` - Added watermark system  
`v2.0` - Complete redesign with Rich UI  

---
Apache 2.0 License | Commercial Use Allowed | Attribution Required
---

<p align="center">
  Built with ❤️ by <a href="https://github.com/rexuraa">@rexuraa</a> | 
  <a href="https://github.com/rexuraa/xtrime_downloader/issues">Report Issues</a> | 
  <a href="https://github.com/rexuraa/xtrime_downloader/stargazers">⭐ Star Project</a>
</p>

