import os
import requests
import json
import base64
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, AudioClip, concatenate_audioclips
from dotenv import load_dotenv
from moviepy.config import change_settings
import matplotlib.image as mpimg
import numpy as np
import datetime
import re

# Update this path to where ImageMagick is installed on your system
IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

load_dotenv()
# ElevenLabs API Key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_KEY")
VOICE_ID = "EGQM7bHbTHTb7VUEcOHG"  # Using voice ID from tts.py

def clean_text_for_display(text):
    # Remove break tags from text for display purposes
    # Match break tags with optional spaces and any time value
    cleaned_text = re.sub(r'\s*<break\s+time=[\'"]\d+\.?\d*s?[\'"]>\s*', ' ', text)
    return cleaned_text

def insert_break_at_middle(text, break_time=1.0):
    """
    Insert a break tag near the middle of the text at the nearest space.
    
    Args:
        text (str): Input text
        break_time (float): Break duration in seconds
        
    Returns:
        str: Text with break tag inserted
    """
    # Find the middle position
    mid_pos = len(text) // 2
    
    # Find the nearest space before or after the middle
    left_space = text.rfind(' ', 0, mid_pos)
    right_space = text.find(' ', mid_pos)
    
    # Choose the closest space to the middle
    if left_space == -1:
        insert_pos = right_space if right_space != -1 else mid_pos
    elif right_space == -1:
        insert_pos = left_space
    else:
        insert_pos = left_space if (mid_pos - left_space) <= (right_space - mid_pos) else right_space
    
    # Insert the break tag without extra spaces
    return f"{text[:insert_pos]}<break time='{break_time}s'>{text[insert_pos:]}"


def create_reel(title, display_text, speech_text=None, background_image_path="background.jpg",
               font_size=80, text_color='white', stroke_color='white', offset_time=0.5, y_offset=0):
    """
    Create an Instagram-style reel with text-to-speech narration
    
    Args:
        title (str): Title of the reel (used for output filenames)
        display_text (str): Text to display in the reel
        speech_text (str, optional): Text to use for text-to-speech narration. If None, display_text will be used.
        background_image_path (str): Path to background image
        text_color (str): Color of the text (default: 'white')
        stroke_color (str): Color of the text stroke/outline (default: 'white')
        offset_time (float): Silent time at start and end of video (default: 0.5)
        y_offset (int): Vertical offset from center in pixels. Positive moves down, negative moves up (default: 0)
        
    Returns:
        tuple: (success (bool), message (str))
    """
    # Create reels directory if it doesn't exist
    reels_dir = "reels"
    os.makedirs(reels_dir, exist_ok=True)
    
    # Setup output paths
    output_audio_path = os.path.join(reels_dir,"vids", f"{title}_audio.mp3")
    output_video_path = os.path.join(reels_dir,"vids", f"{title}_reel.mp4")
    
    # If speech_text is not provided, use display_text
    if speech_text is None:
        speech_text = display_text
    
    # Clean display text for visual display
    display_text = clean_text_for_display(display_text)
    
    # Generate TTS using ElevenLabs
    def generate_tts(text, output_path):
        # Check if audio file already exists
        if os.path.exists(output_path):
            print(f"Using existing audio file: {output_path}")
            return True

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                # Parse response and get base64 audio
                json_string = response.content.decode("utf-8")
                response_dict = json.loads(json_string)
                audio_bytes = base64.b64decode(response_dict["audio_base64"])
                
                # Save audio file
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)
                print("TTS audio saved successfully.")
                
                # Save alignment data for potential future use
                alignment_path = output_path.replace(".mp3", "_alignment.txt")
                with open(alignment_path, "w") as f:
                    f.write(str(response_dict["alignment"]))
                return True
            else:
                print(f"Error: {response.status_code}", response.json())
                return False
        except Exception as e:
            print(f"Error generating TTS: {str(e)}")
            return False

    # Get Duration of Audio File
    def get_audio_duration(audio_path):
        try:
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            return duration
        except Exception as e:
            print(f"Error getting audio duration: {str(e)}")
            return None

    # Create Animated Text Clip
    def create_text_clip(text, duration, fps=30):
        try:
            # Use display_text instead of original text
            text_clip = TextClip(
                text,
                fontsize=font_size,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=2,
                font="Arial-Bold",
                method='caption',
                size=(1080, None),  # Width of 1080, height automatic
                align='center'
            )
            
            # Calculate text positions
            video_height = 1920
            text_height = text_clip.h
            y_position = (video_height - text_height) // 2 + y_offset  # Add y_offset to center position
            
            # Set the text position
            text_clip = text_clip.set_position(('center', y_position))
            
            # Set duration
            text_clip = text_clip.set_duration(duration)
            
            # Add fade effects
            text_clip = text_clip.fadein(0.5).fadeout(0.5)
            
            return text_clip
        except Exception as e:
            print(f"Error creating text clip: {str(e)}")
            return None

    def create_text_clips_from_alignment(alignment_path, duration):
        try:
            print("Starting text clip creation...")
            # Read alignment data
            with open(alignment_path, 'r') as f:
                alignment = eval(f.read())
            
            # Extract character data
            chars = alignment['characters']
            start_times = alignment['character_start_times_seconds']
            end_times = alignment['character_end_times_seconds']
            
            print(f"\nDebug - Audio duration: {duration}")
            print(f"Debug - Total video duration: {duration + 2*offset_time}")
            print(f"Debug - First char starts at: {start_times[0]}")
            print(f"Debug - Last char ends at: {end_times[-1]}")
            print(f"Debug - Total characters: {len(chars)}")
            
            # Get the cleaned display text
            display_words = display_text.split()
            print(f"Debug - Display words: {display_words}")
            
            # Initialize lists for word timings
            word_start_times = []
            word_end_times = []
            
            # Helper function to skip break tag characters
            def skip_break_tag(index):
                initial_index = index
                while index < len(chars) and chars[index] == '<':
                    # Skip until we find '>'
                    while index < len(chars) and chars[index] != '>':
                        index += 1
                        if index - initial_index > 50:  # Safety check
                            print(f"Warning: Break tag too long or missing closing tag at index {initial_index}")
                            return initial_index
                    # Skip the '>' character
                    index += 1
                    # Skip any following spaces
                    while index < len(chars) and chars[index] == ' ':
                        index += 1
                return index
            
            # Map the alignment timing to cleaned text
            current_char_index = 0
            
            print("Starting word timing mapping...")
            # For each word in display text
            for word_idx, word in enumerate(display_words):
                print(f"Processing word {word_idx + 1}/{len(display_words)}: '{word}'")
                
                # Skip any spaces and break tags before the word
                while current_char_index < len(chars) and (chars[current_char_index] == ' ' or chars[current_char_index] == '<'):
                    old_index = current_char_index
                    current_char_index = skip_break_tag(current_char_index)
                    if current_char_index == old_index:  # If no progress was made
                        current_char_index += 1  # Force progress
                
                if current_char_index < len(chars):
                    print(f"  Word starts at char index {current_char_index} ('{chars[current_char_index]}')")
                    # Store start time of first character of word
                    word_start_times.append(start_times[current_char_index])
                    
                    # Find corresponding word in original text
                    word_length = len(word)
                    end_char_index = current_char_index
                    chars_matched = 0
                    
                    # Match characters until we find all characters of the word
                    safety_counter = 0
                    while end_char_index < len(chars) and chars_matched < word_length:
                        safety_counter += 1
                        if safety_counter > 100:  # Safety check
                            print(f"Warning: Possible infinite loop while matching word '{word}'")
                            break
                            
                        if chars[end_char_index] != '<':  # Skip break tags
                            chars_matched += 1
                        else:
                            # Skip the entire break tag
                            old_index = end_char_index
                            end_char_index = skip_break_tag(end_char_index)
                            if end_char_index == old_index:  # If no progress was made
                                end_char_index += 1  # Force progress
                            continue
                        end_char_index += 1
                    
                    # Adjust end_char_index to point to last character of word
                    end_char_index = min(end_char_index - 1, len(end_times) - 1)
                    word_end_times.append(end_times[end_char_index])
                    print(f"  Word ends at char index {end_char_index} ('{chars[end_char_index]}')")
                    
                    # Move current_char_index to after this word
                    current_char_index = end_char_index + 1
            
            print("Word timing mapping completed.")
            print(f"Debug - Display Words: {display_words}")
            print(f"Debug - Word start times: {word_start_times}")
            print(f"Debug - Word end times: {word_end_times}")
            
            print("Creating text clips...")
            # Create clips for each word
            clips = []
            for i in range(len(display_words)):
                print(f"Creating clip for word: {display_words[i]}")
                # Create text with all words up to current word
                text = ' '.join(display_words[:i+1])
                word_clip = TextClip(
                    text,
                    fontsize=font_size,
                    color=text_color,
                    stroke_color=stroke_color,
                    stroke_width=2,
                    font="Arial-Bold",
                    method='caption',
                    size=(1080, None),
                    align='center'
                )
                
                # Calculate text positions
                video_height = 1920
                text_height = word_clip.h
                y_position = (video_height - text_height) // 2 + y_offset  # Add y_offset to center position
                
                # Set the text position
                word_clip = word_clip.set_position(('center', y_position))
                
                # Set timing for this clip
                start = word_start_times[i]
                end = word_start_times[i+1] if i < len(display_words)-1 else word_end_times[i]
                
                word_clip = word_clip.set_start(start + offset_time)
                word_clip = word_clip.set_duration(end - start)
                
                print(f"Clip {i} - Text: '{text}' - Start: {start + offset_time:.2f} - End: {end + offset_time:.2f}")
                clips.append(word_clip)
            
            print("Creating final text clip...")
            # Add a final clip with complete text that stays until the end
            final_text = ' '.join(display_words)
            final_clip = TextClip(
                final_text,
                fontsize=font_size,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=2,
                font="Arial-Bold",
                method='caption',
                size=(1080, None),
                align='center'
            )
            
            # Calculate text positions
            video_height = 1920
            text_height = final_clip.h
            y_position = (video_height - text_height) // 2 + y_offset  # Add y_offset to center position
            
            # Set the text position
            final_clip = final_clip.set_position(('center', y_position))
            
            # Calculate timings for final clip
            total_duration = duration + 2*offset_time  # offset_time before + offset_time after
            
            # Start showing final text when last word ends
            final_start = word_end_times[-1] + offset_time
            # Show until the very end of video
            final_duration = total_duration - final_start
            
            print("\n=== Final Clip Debug ===")
            print(f"Total duration: {total_duration:.2f}s")
            print(f"Last word ends at: {word_end_times[-1]:.2f}s")
            print(f"Final clip starts at: {final_start:.2f}s")
            print(f"Final clip duration: {final_duration:.2f}s")
            print(f"Final clip ends at: {final_start + final_duration:.2f}s")
            print("=======================\n")
            
            # Create the final clip that shows until the end
            final_clip = final_clip.set_start(final_start)
            final_clip = final_clip.set_duration(final_duration)
            
            # Add both the word clips and the final clip
            all_clips = clips + [final_clip]
            
            return all_clips
        except Exception as e:
            print(f"Error creating word clips: {str(e)}")
            return None

    try:
        # Generate TTS audio
        if not generate_tts(speech_text, output_audio_path):
            return False, "Failed to generate audio"

        # Get audio duration
        duration = get_audio_duration(output_audio_path)
        if duration is None:
            return False, "Failed to get audio duration"

        # Load background image
        try:
            print(f"Loading background image from: {background_image_path}")
            background = ImageClip(background_image_path)
            print(f"Original background size: {background.size}")
            
            # Calculate dimensions to fill 1080x1920 while maintaining aspect ratio
            img_ratio = background.size[0] / background.size[1]
            target_ratio = 1080 / 1920

            if img_ratio > target_ratio:
                # Image is wider than needed
                new_height = 1920
                new_width = int(new_height * img_ratio)
            else:
                # Image is taller than needed
                new_width = 1080
                new_height = int(new_width / img_ratio)

            print(f"Resizing to: {new_width}x{new_height}")
            background = background.resize((new_width, new_height))
            print(f"After resize: {background.size}")
            
            # Create a black background of target size
            black_bg = ColorClip(size=(1080, 1920), color=(0,0,0))
            
            # Center the image on black background
            x_center = (1080 - new_width) // 2
            y_center = (1920 - new_height) // 2
            background = background.set_position((x_center, y_center))
            
            # Load audio and get durations
            audio = AudioFileClip(output_audio_path)
            audio_duration = audio.duration
            total_duration = audio_duration + 2*offset_time  # offset_time before + offset_time after
            
            # Create silent audio for the offset
            silent_audio = AudioClip(make_frame=lambda t: 0, duration=offset_time)
            # Concatenate silent audio at the start
            audio = concatenate_audioclips([silent_audio, audio])
            
            # Set durations for all clips
            black_bg = black_bg.set_duration(total_duration)
            background = background.set_duration(total_duration)
            
            # Create the background composite (black bg + image)
            background_composite = CompositeVideoClip([black_bg, background])
            background_composite = background_composite.set_duration(total_duration)
            background_composite = background_composite.set_audio(audio)
            
            # Load and prepare company logo based on text color
            logo_path = "crackkar_logo_white.png" if text_color.lower() == 'white' else "crackkar_logo_black.png"
            logo = ImageClip(logo_path)
            logo = logo.resize((200, 200))  # Make logo square 200x200
            # Position at bottom left with some padding (20 pixels from edges)
            logo = logo.set_position((20, 1920 - 200 - 20))
            logo = logo.set_duration(total_duration)

            # Website URL

            website_url = "www.crackkar.com"
            website = TextClip(
                website_url,
                fontsize=50,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=2,
                font="Arial-Bold",
                method='caption',
                size=(1080, None),
                align='center'
            )
            
            # Calculate text positions
            video_height = 1920
            text_height = website.h
            y_position = 1920 - 100 - 40  # Position at bottom
            
            # Set the text position
            website = website.set_position(('center', y_position))
            
            # Set duration
            website = website.set_duration(total_duration)

            # Prompt to check caption for poll
            caption_text = "(Check caption for options)"
            caption_clip = TextClip(
                caption_text,
                fontsize=45,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=2,
                font="Arial-Bold",
                method='caption',
                size=(1080, None),
                align='center'
            )
            caption_clip = caption_clip.set_position(('center', y_position - 200))
            caption_clip = caption_clip.set_duration(total_duration)

            # UPSC CSE prep disclaimer
            disclaimer_text = "UPSC-CSE 2025 Prep."
            disclaimer_clip = TextClip(
                disclaimer_text,
                fontsize=55,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=2,
                font="Arial-Bold",
                method='caption',
                size=(1080, None),
                align='center'
            )
            disclaimer_clip = disclaimer_clip.set_position(('center', y_position - 300))
            disclaimer_clip = disclaimer_clip.set_duration(total_duration)
            
            # Create word-by-word text animation
            alignment_path = output_audio_path.replace(".mp3", "_alignment.txt")
            text_clips = create_text_clips_from_alignment(alignment_path, audio_duration)
            if text_clips is None:
                return False, "Failed to create text animation"
            
            # Combine all clips
            final_clip = CompositeVideoClip(
                [background_composite, logo, website,caption_clip, disclaimer_clip] + text_clips,
                size=(1080, 1920)
            ).set_duration(total_duration)
            
            # Export video with progress bar
            print("Creating video... This may take a few minutes.")
            final_clip.write_videofile(
                output_video_path,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                threads=4
            )
            print(f"Video successfully created at {output_video_path}")
            return True, f"Successfully created reel at {output_video_path}"
        except Exception as e:
            return False, f"Error loading background image: {str(e)}"
    except Exception as e:
        return False, f"Error in video creation process: {str(e)}"

if __name__ == "__main__":
    # Example usage
    today_date=datetime.date.today().strftime("%d-%m-%Y")
    title = f"{today_date}_mcq_reel"
    display_text = insert_break_at_middle("Which of the following is true for Grok 3 ?")
    speech_text = insert_break_at_middle("Which of the following is true for Grok 3 ?")
    
    font_size=65
    background_path=os.path.join("reels","bg_images","grok_bg.jpg")
    text_color='white'
    stroke_color='white'
    offset_time=0.75
    y_offset=-100
    success, message = create_reel(title=title, display_text=display_text, speech_text=speech_text, background_image_path=background_path,
                                 font_size=font_size, text_color=text_color, stroke_color=stroke_color,
                                 offset_time=offset_time, y_offset=y_offset)
    print(message)
