# AI Recipes

A collection of AI-powered content creation tools.

## Project Structure

### 1. Long Form Content Generation
Located in `1_ Long Form Content Generation/`

A tool for generating extensive long-form content using AI language models. Features:
- Utilizes both Gemini-1.5-Pro and Command R+ models
- Iterative content generation with context preservation
- Research material generation capability
- Rate-limited for API compliance

[Learn more about Long Form Content Generation](./1_%20Long%20Form%20Content%20Generation/README.md)

### 2. Reel Creation
Located in `2_Reel Creation/`

A tool for creating Instagram-style reels with AI-powered text-to-speech. Features:
- Text-to-speech using ElevenLabs API
- Animated text overlays
- Custom video formatting for social media
- Synchronized audio-visual content

[Learn more about Reel Creation](./2_Reel%20Creation/README.md)

## Dependencies

### Core Python Packages
- `google.generativeai`
- `cohere`
- `moviepy`
- `python-dotenv`
- `requests`
- `numpy`
- `matplotlib`

### External Dependencies
- ImageMagick (required for Reel Creation)

## Setup

1. Install required Python packages:
```bash
pip install google-generativeai cohere moviepy python-dotenv requests numpy matplotlib
```

2. Install ImageMagick (required for Reel Creation)

3. Create a `.env` file with the following API keys:
```
GEMINI_KEY=your_gemini_api_key
COHERE_KEY=your_cohere_api_key
ELEVENLABS_KEY=your_elevenlabs_api_key
```

4. Update the ImageMagick binary path in `2_Reel Creation/content.py`

## Usage

Each module has its own documentation with detailed usage instructions. See the respective README.md files in each directory.
