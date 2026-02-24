import sys
import os
import subprocess
import glob

try:
    import imageio_ffmpeg
except ImportError:
    print("Error: Run 'pip install imageio-ffmpeg' first.")
    sys.exit(1)

def compress_video(input_file, compression_level=28):
    if not os.path.exists(input_file):
        print(f"⚠️ Error: '{input_file}' not found. Skipping...")
        return

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_compressed.mp4"

    print(f"\n▶️ STARTING COMPRESSION: {input_file}")
    print(f"Level: {compression_level} | Target: {output_file}")

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
        subprocess.run(cmd, check=True)
        
        original_size = os.path.getsize(input_file)
        new_size = os.path.getsize(output_file)
        savings = (1 - (new_size / original_size)) * 100
        
        print(f"\n✅ FINISHED: {input_file}")
        print(f"Original size: {original_size / (1024*1024):.2f} MB")
        print(f"New size:      {new_size / (1024*1024):.2f} MB")
        print(f"Reduced by:    {savings:.1f}%\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during compression of {input_file}: {e}")

if __name__ == "__main__":
    # Get all arguments passed in the terminal (ignoring the script name itself)
    args = sys.argv[1:]
    
    files_to_process = []
    compression_level = 28 # Default reduction
    
    if not args:
        # If you just type 'python compress.py', auto-detect all MOV files
        print("Auto-detecting all .MOV files in the current folder...")
        files_to_process = glob.glob("*.MOV") + glob.glob("*.mov")
    else:
        # Check if the very last argument is a number (for custom compression)
        if args[-1].isdigit():
            compression_level = int(args.pop())
            
        # If files were manually specified, use those. Otherwise, auto-detect.
        if args:
            files_to_process = args
        else:
            files_to_process = glob.glob("*.MOV") + glob.glob("*.mov")

    # Exit if no files are found
    if not files_to_process:
        print("No .MOV files found to process.")
        sys.exit(0)

    print(f"Found {len(files_to_process)} video(s) to compress.")
    print("=" * 40)
    # Loop through the list and process each one
    for file in files_to_process:
        compress_video(file, compression_level)
        print("-" * 40)
        
    print("\n🎉 ALL VIDEOS HAVE BEEN COMPRESSED!")