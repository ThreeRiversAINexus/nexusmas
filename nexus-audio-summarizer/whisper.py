import os
import openai
from pydub import AudioSegment
import uuid

def transcribe_audio_file(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        # Replace the following line with the actual call to transcribe
        # the audio file using OpenAI or any other service
        print("Transcribing file: " + audio_file_path)
        try:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript["text"]
        except:
            print("Error transcribing file: " + audio_file_path)
        return ""

def transcribe_all_audio_files_in_dir(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".mp3"):
                audio_file_path = os.path.join(root, file)
                transcript = transcribe_audio_file(audio_file_path)

                # Write the transcript to a .txt file of the same name
                parent_dir = os.path.dirname(os.path.dirname(audio_file_path))
                transcript_file_path = os.path.join(parent_dir, "text_transcripts", os.path.splitext(file)[0] + '.txt')
                with open(transcript_file_path, 'w') as transcript_file:
                    transcript_file.write(transcript)

def split_audio(audio_file_path, audio_chunk_dir):
    # Load m4a file
    audio = AudioSegment.from_file(audio_file_path, "m4a")

    # Length of audio in milliseconds
    length_audio = len(audio)

    # Start and end times
    start = 0
    # 1 minute in milliseconds
    end = 60 * 1000

    # Get the original file base name (without extension)
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]

    count = 0
    # Start creating chunks
    while start < length_audio:
        print("Creating chunk " + str(count) + " for file " )
        # Creating chunk
        chunk = audio[start:end]

        # Filename / Path to export the chunk
        chunk_filename = os.path.join(audio_chunk_dir, f"{base_name}_audio_{count:03d}.mp3")

        # Export chunk audio
        print("Exporting chunk")
        chunk.export(chunk_filename, format="mp3")

        # Next chunk
        count += 1
        start += 60 * 1000
        end += 60 * 1000

def process_all_audio_files_in_dir(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".m4a"):
                from pprint import pprint
                pprint("Working on file: " + file)
                audio_file_path = os.path.join(root, file)
                
                # Create a new random directory for each m4a file
                parent_dir = os.path.dirname(root)
                new_dir = os.path.join(parent_dir, "done", uuid.uuid4().hex[:6])
                os.makedirs(new_dir, exist_ok=True)

                # Create subdirectories for audio chunks and text transcripts
                audio_chunk_dir = os.path.join(new_dir, "audio_chunks")
                os.makedirs(audio_chunk_dir, exist_ok=True)

                text_transcript_dir = os.path.join(new_dir, "text_transcripts")
                os.makedirs(text_transcript_dir, exist_ok=True)

                # Split audio into 1-minute chunks
                split_audio(audio_file_path, audio_chunk_dir)
                print("Done splitting audio up")
                
                # Now you would need to call your transcribe function on each of the split files
                # and save the transcriptions into the text_transcript_dir
                print("Transcribing audio chunks...")
                transcribe_all_audio_files_in_dir(audio_chunk_dir)

dir_path = "example_client_knowledgebase/audios/"
process_all_audio_files_in_dir(dir_path)
