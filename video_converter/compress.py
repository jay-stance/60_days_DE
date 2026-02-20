import sys
import os
import subprocess
try:
    import imageio_ffmpeg
except ImportError:
    print("Error: Run 'pip install imageio-ffmpeg' first.")
    sys.exit(1)

def compress_video(input_file, compression_level=28):
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found.")
        return

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_compressed.mp4"

    print(f"--- STARTING COMPRESSION ---")
    print(f"Input: {input_file}")
    print(f"Compression Level: {compression_level} (Standard=23, High=28)")
    print("NOTE: This will take time depending on your CPU speed.")
    print("----------------------------")

    # Command breakdown:
    # -c:v libx264: Use the H.264 video compressor (industry standard)
    # -crf: The quality setting. Higher number = more compression.
    # -preset faster: Speeds up the process (sacrifices a tiny bit of compression for speed)
    # -c:a aac: Compress audio to AAC
    cmd = [
        ffmpeg_exe,
        '-y',
        '-i', input_file,
        '-c:v', 'libx264',
        '-crf', str(compression_level),
        '-preset', 'faster', 
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        output_file
    ]

    try:
        # Run FFmpeg
        subprocess.run(cmd, check=True)
        
        # Calculate savings
        original_size = os.path.getsize(input_file)
        new_size = os.path.getsize(output_file)
        savings = (1 - (new_size / original_size)) * 100
        
        print(f"\n✅ DONE!")
        print(f"Saved as: {output_file}")
        print(f"Original size: {original_size / (1024*1024):.2f} MB")
        print(f"New size:      {new_size / (1024*1024):.2f} MB")
        print(f"Reduced by:    {savings:.1f}%")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during compression: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress.py <filename> [compression_level]")
        print("Example: python compress.py myvideo.mov 30")
    else:
        file_path = sys.argv[1]
        
        # Check if user provided a specific compression level
        if len(sys.argv) > 2:
            level = int(sys.argv[2])
        else:
            level = 28 # Default "Drastic" reduction
            
        compress_video(file_path, level)