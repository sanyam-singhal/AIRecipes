# Reel Creation Module

This module provides functionality for creating Instagram-style reels with text-to-speech narration and animated text overlays.

## Dependencies

- `moviepy`: For video editing and creation
- `requests`: For making HTTP requests to ElevenLabs API
- `python-dotenv`: For loading environment variables
- `numpy`: For image processing
- `matplotlib`: For image handling
- `ImageMagick`: Required for text rendering (must be installed separately)

## Environment Setup

1. Install ImageMagick and update `IMAGEMAGICK_BINARY` path in the script
2. Set up environment variables in `.env` file:
   - `ELEVENLABS_KEY`: API key for ElevenLabs text-to-speech service

## Brand Configuration

At the top of the script, configure your brand details:
```python
brand_name = "Your Brand Name"
white_logo_path = "path/to/white_logo.png"  # For dark backgrounds with white font color
black_logo_path = "path/to/black_logo.png"  # For light backgrounds with black font color
website_url = "www.yourdomain.com"
```

## Core Features

### Text Processing
- `clean_text_for_display()`: Removes break tags from text
- `insert_break_at_middle()`: Inserts speech breaks at optimal positions for natural narration

### Reel Creation
The main function `create_reel()` handles:
1. Text-to-speech generation using ElevenLabs API
2. Animated text overlay creation with word-by-word animation
3. Video composition with background image
4. Audio-visual synchronization
5. Brand elements placement (logo and website URL)

#### Parameters
- `title`: Output filename prefix
- `display_text`: Text to show in the video
- `speech_text`: Optional text for narration (defaults to display_text)
- `background_image_path`: Path to background image
- `font_size`: Text size (default: 80)
- `text_color`: Text color (default: white)
- `stroke_color`: Text outline color (default: white)
- `offset_time`: Silent padding at start/end (default: 0.5s)
- `y_offset`: Vertical text position adjustment

## Technical Details

### Video Specifications
- Resolution: 1080x1920 (Instagram Reel format)
- Text Animation: 
  - Word-by-word appearance
  - Fade in/out effects
  - Synchronized with speech
- Text Positioning: Centered with customizable vertical offset
- Audio: MP3 format with timestamps for synchronization
- Brand Elements:
  - Logo (200x200px) positioned at bottom left
  - Website URL at bottom center
  - Adaptive logo color based on text color

### Text-to-Speech Integration
- Uses ElevenLabs API with customizable voice ID
- Supports SSML-style break tags for pacing
- Includes timestamp alignment data
- Caches generated audio files

## Output Structure
```
reels/
├── vids/
│   ├── {title}_audio.mp3
│   ├── {title}_audio_alignment.txt
│   └── {title}_reel.mp4
```

## Best Practices

1. Background Images:
   - Use high-quality images
   - Ensure good contrast with text
   - Consider aspect ratio (portrait orientation)

2. Text Content:
   - Keep text concise and readable
   - Test different font sizes (50-70 for long text, 70-100 for short)
   - Use breaks for natural speech pacing

3. Branding:
   - Prepare both light and dark versions of your logo
   - Ensure logo is visible against background
   - Keep website URL readable

4. Performance:
   - Monitor ElevenLabs API usage
   - Cache generated audio when possible
   - Consider memory usage for long videos

## Limitations

1. Requires ImageMagick installation
2. Subject to ElevenLabs API limits
3. Memory intensive for long videos
4. Limited to vertical (portrait) format
5. Fixed logo size and position

## Example Usage

```python
title = f"{datetime.date.today().strftime('%d-%m-%Y')}_example_reel"
display_text = "What makes artificial intelligence so fascinating?"
background_path = os.path.join("reels", "bg_images", "default_background.jpg")

success, message = create_reel(
    title=title,
    display_text=display_text,
    background_image_path=background_path,
    font_size=65,
    text_color='white',
    stroke_color='white',
    offset_time=0.75,
    y_offset=-100
)