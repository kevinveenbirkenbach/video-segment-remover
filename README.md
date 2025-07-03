# 📹 Video Segment Remover (Visere)

A simple Python CLI tool to remove specified time ranges from video files, built with FFmpeg.

---

## ⚙️ Installation

Install using Kevin’s Package Manager under the alias **visere**:

```bash
visere install video-segment-remover
```

---

## 🚀 Usage

After installation, run:

```bash
visere video-segment-remover --help
```

to see all available commands and options. For example:

```bash
visere video-segment-remover input.mp4 --from 00:02:00 --to 00:03:30
```

This will remove the segment between **00:02:00** and **00:03:30** and save the result as `input.new.mp4`.

---

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute! 🎉

> Developed by [Kevin Veen-Birkenbach](https://www.veen.world)
