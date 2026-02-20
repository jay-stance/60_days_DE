import sys
import os
import subprocess
import imageio_ffmpeg # This is the tool you just installed

def convert_mov_to_mp4(input_file):
    # 1. verify input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' was not found.")
        return

    # 2. auto-detect the ffmpeg binary you just installed
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"ffmpeg found at: {ffmpeg_exe}")

    # 3. determine output filename
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}.mp4"

    print(f"Converting '{input_file}' -> '{output_file}'...")
    print("This will be fast (copying stream only)...")

    # 4. construct the command
    # -y means overwrite output if it exists
    # -c copy means NO re-encoding (lossless + fast)
    cmd = [
        ffmpeg_exe, 
        '-y', 
        '-i', input_file, 
        '-c', 'copy', 
        '-movflags', '+faststart', 
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Done! Saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Conversion failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert.py <filename>")
    else:
        convert_mov_to_mp4(sys.argv[1])