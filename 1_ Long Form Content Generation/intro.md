# Long form content generation

## Introduction

Exploring content creation using LLMs where the required content length exceeds the current LLM output context window.

The idea used here is simple, leverage the large input window to recursively create content.

This would application in script creations, article writing, where the model would assist their human user in creating the content

## Dependencies

The current script tries the approach with Gemini-1.5 and Command R series:

```
pip install google-generativeai
pip install cohere
```

Apart from that, using `dotenv` for environment variables.