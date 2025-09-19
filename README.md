Video Creator with Streamlit and FFmpeg

This is a Streamlit application that allows you to generate a video from a set of images and audio files. It automatically synchronizes the duration of each image with its corresponding audio track, creating a professional-looking video with fade-in and fade-out effects.

🚀 Features
User-Friendly Interface: Upload audio and image files directly from your browser.

Audio-Image Synchronization: Each image is displayed for the exact duration of its corresponding audio file.

FFmpeg Integration: Leverages FFmpeg for robust and efficient video and audio processing.

Progress Tracking: Real-time progress bars show the status of the video creation and merging process.

Automatic Cleanup: Temporary files and folders are automatically removed after the process is complete.

📦 Prerequisites
To run this application, you need to have the following installed on your system:

Python 3.x: The core language for the application.

FFmpeg: The command-line tool for handling video and audio. Ensure it is installed and added to your system's PATH. You can download it from the official FFmpeg website.

🔧 Installation and Setup
Clone the repository (or save the files manually):

Save the provided app.py and requirements.txt files in the same directory.

Install Python packages:

Open your terminal or command prompt in the project directory and install the required libraries using pip.

Bash

pip install -r requirements.txt
Run the application:

Execute the following command in your terminal to start the Streamlit app.

Bash

streamlit run app.py
This will open the application in your default web browser.

📝 Usage
Open the App: Run the streamlit run app.py command.

Upload Files:

Use the "Upload Audio Files (MP3)" uploader to select your audio tracks. The application will sort them numerically (e.g., track1.mp3, track2.mp3).

Use the "Upload Image Files (JPG, PNG)" uploader to select your images. Ensure you have at least as many images as audio files. The images will also be sorted numerically.

Generate Video: Click the "Generate Video" button. The app will show progress bars for each step.

Download: Once the process is complete, a "Download Video" button will appear. Click it to save your final video.

📂 Project Structure
.
├── app.py              # The main Streamlit application script
├── requirements.txt    # Lists the required Python packages
└── README.md           # This file
Troubleshooting
"FFmpeg not found" error: Make sure FFmpeg is installed and its directory is included in your system's PATH environment variable.

"Error during video creation": Check your terminal for detailed FFmpeg error messages. This can be caused by unsupported file formats or corrupted files.
