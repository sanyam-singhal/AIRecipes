# Long Form Content Generation

This module provides functionality for generating extensive long-form content using AI language models (Gemini-1.5-Pro and Command R+).

## Dependencies

- `google.generativeai`: Google's Gemini API client
- `cohere`: Cohere's API client for Command R+
- `python-dotenv`: For loading environment variables
- `time`: For managing API rate limits

## Environment Setup

The following environment variables need to be set in a `.env` file:
- `GEMINI_KEY`: API key for Google's Gemini
- `COHERE_KEY`: API key for Cohere

## Core Features

### Research Material Generation
- Two implementations available:
  1. `generate_research_material_gemini()`: Uses Gemini-1.5-Pro
  2. `generate_research_material_cohere()`: Uses Command R+
- Both functions take a user prompt and return research material for long-form content

### Long Form Content Generation
- Two implementations available:
  1. `generate_long_form_content_gemini()`: Uses Gemini-1.5-Pro
  2. `generate_long_form_content_cohere()`: Uses Command R+
- Features:
  - Iterative generation up to `max_iterations` (default: 15)
  - 45-second delay between iterations to avoid API rate limits
  - Maximum output of 4096 tokens per generation
  - Temperature setting of 0.75 for creative content
  - Maintains context across iterations for coherent content

## Usage

1. Set up environment variables in `.env` file
2. Run the script and input your content prompt
3. The script will:
   - Generate initial research material
   - Iteratively generate long-form content
   - Save output to either `cohere_longform.txt` or `gemini_longform.txt`

## Technical Details

- **Token Limits**:
  - Command R+: 4k output window
  - Gemini: 8k window
  - Maximum output length = 4k * max_iterations

- **Rate Limiting**: 
  - 45-second delay between generations
  - Helps avoid free API rate limits
  - Suitable for non-latency-critical applications

## Best Practices

1. Use specific, detailed prompts for better content generation
2. Consider the total token length (4k * max_iterations) when setting parameters
3. Monitor API usage and adjust delays if needed
4. Use generated content as a foundation for human editing/refinement

## Limitations

1. Output quality may not match human-written content
2. Best used as a starting point for creative work
3. Subject to API rate limits and token constraints
4. Requires careful prompt engineering for optimal results