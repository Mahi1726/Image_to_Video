import streamlit as st
import subprocess
import os
import shutil
import json

# --- File Paths ---
TEMP_DIR = "temp"
OUTPUT_VIDEO = "output.mp4"

# --- Helper Functions ---
def get_file_paths(file_list):
    """Saves uploaded files to a temporary directory and returns their paths."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    paths = []
    for uploaded_file in file_list:
        file_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(file_path)
    # The sorted() function here correctly handles numeric sorting like file1, file2, file10
    return sorted(paths)

def get_audio_durations(audio_paths):
    """Uses ffprobe to get the duration of each audio file."""
    durations = []
    for audio_path in audio_paths:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", audio_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            duration = float(metadata["format"]["duration"])
            durations.append(duration)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            st.error(f"❌ Error getting duration for {os.path.basename(audio_path)}: {e}")
            return None
    return durations

def create_video(image_paths, durations, progress_bar):
    """Creates a video from a sequence of images with specified durations and fade effects."""
    st.info("🎬 Creating video from images...")
    
    filter_lines = []
    for i, dur in enumerate(durations):
        fade_dur = min(1, dur / 2)
        fade_out_start = dur - fade_dur
        filter_lines.append(
            f"[{i}:v]fade=t=in:st=0:d={fade_dur:.2f},fade=t=out:st={fade_out_start:.2f}:d={fade_dur:.2f}[v{i}]"
        )
    
    concat_inputs = "".join([f"[v{i}]" for i in range(len(durations))])
    complex_filter = f"{';'.join(filter_lines)};{concat_inputs}concat=n={len(durations)}:v=1:a=0[v]"
    
    temp_video = os.path.join(TEMP_DIR, "temp_video.mp4")
    
    cmd = ["ffmpeg"]
    for i, img_path in enumerate(image_paths):
        cmd.extend(["-loop", "1", "-t", str(durations[i]), "-i", img_path])
        
    cmd.extend([
        "-filter_complex", complex_filter,
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-r", "30",
        "-y", temp_video
    ])
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            if "frame=" in line:
                try:
                    frame_match = line.split("frame=")[-1].strip().split(" ")[0]
                    if frame_match.isdigit():
                        frame = int(frame_match)
                        total_frames = int(sum(durations) * 30) # 30 fps
                        progress_value = min(frame / total_frames, 1.0)
                        progress_bar.progress(progress_value, text=f"Creating video... {int(progress_value*100)}%")
                except:
                    pass
        process.wait()
        
        if process.returncode != 0:
            st.error("❌ Error during video creation. Check console for FFmpeg output.")
            return None
        return temp_video
    except Exception as e:
        st.error(f"❌ Failed to run FFmpeg command: {e}")
        return None

def merge_video_audio(temp_video, audio_paths, total_duration, progress_bar):
    """Merges the temporary video and audio files."""
    st.info("🔄 Merging video and audio...")
    temp_audio = os.path.join(TEMP_DIR, "temp_audio.m4a")
    
    # Create the audio file list
    audio_list_path = os.path.join(TEMP_DIR, "audio_list.txt")
    with open(audio_list_path, "w") as f:
        for audio_path in audio_paths:
            f.write(f"file '{os.path.abspath(audio_path)}'\n")

    # Merge all audio files into a single temporary audio file
    audio_cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", audio_list_path,
        "-c:a", "aac",
        "-b:a", "192k",
        "-y", temp_audio
    ]
    subprocess.run(audio_cmd, check=True)
    
    # Merge temporary video and audio
    cmd = [
        "ffmpeg", "-i", temp_video, "-i", temp_audio,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-t", str(total_duration),
        "-y", OUTPUT_VIDEO
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            if "time=" in line:
                try:
                    time_match = line.split("time=")[-1].split(" ")[0]
                    h, m, s = map(float, time_match.split(":"))
                    current_time = h * 3600 + m * 60 + s
                    progress_value = min(current_time / total_duration, 1.0)
                    progress_bar.progress(progress_value, text=f"Merging... {int(progress_value*100)}%")
                except:
                    pass
        process.wait()

        if process.returncode != 0:
            st.error("❌ Error during final merge. Check console for FFmpeg output.")
            return False
        return True
    except Exception as e:
        st.error(f"❌ Failed to run FFmpeg command: {e}")
        return False

def clean_up():
    """Removes the temporary directory."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    if os.path.exists(OUTPUT_VIDEO):
        os.remove(OUTPUT_VIDEO)

# --- Streamlit UI ---
st.title("🎬 Video Creation from Audio and Images")

st.markdown("""
Upload your audio and image files to generate a video. 
The video will use each image for the duration of its corresponding audio file.
Files will be sorted numerically (e.g., `audio1.mp3`, `audio2.mp3`).
""")

audio_files = st.file_uploader("Upload Audio Files (MP3)", type=["mp3"], accept_multiple_files=True)
image_files = st.file_uploader("Upload Image Files (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Generate Video"):
    clean_up() # Start with a clean slate
    
    # --- Pre-check ---
    if not audio_files or not image_files:
        st.error("❌ Please upload both audio and image files.")
    elif len(image_files) < len(audio_files):
        st.error("❌ Not enough images! You need at least one image for each audio file.")
    else:
        # --- Main Process ---
        try:
            with st.spinner("Processing..."):
                st.info("Uploading and saving files...")
                audio_paths = get_file_paths(audio_files)
                image_paths = get_file_paths(image_files)
                
                # Get durations
                durations = get_audio_durations(audio_paths)
                if durations is None:
                    # An error occurred, exit gracefully
                    st.stop()

                total_duration = sum(durations)
                st.write(f"🎧 Total audio duration: **{total_duration:.2f} seconds**")
                
                video_progress = st.progress(0, text="Starting video creation...")
                temp_video = create_video(image_paths[:len(audio_files)], durations, video_progress)
                
                if temp_video:
                    final_progress = st.progress(0, text="Starting final merge...")
                    if merge_video_audio(temp_video, audio_paths, total_duration, final_progress):
                        st.balloons()
                        st.success("✅ Video created successfully!")
                        st.download_button(
                            label="Download Video",
                            data=open(OUTPUT_VIDEO, "rb").read(),
                            file_name=OUTPUT_VIDEO,
                            mime="video/mp4"
                        )
                    # Clean up the temporary video file regardless of final merge success
                    os.remove(temp_video) 
        
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        finally:
            clean_up()
