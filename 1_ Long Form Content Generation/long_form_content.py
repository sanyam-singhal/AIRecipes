'''
The onject of this script is to experiment with long form content creation beyond the output context limit using Gemini-1.5-Pro and Command R+

Can we generate cheap (<$15 per million tokens) long form content using Gemini-1.5-Pro and Command R+?

To feed in the model with some summarized research, I have utilized leveraging Gemini-1.5-Pro and Command R+ 
for generating the initial base upon which the long format content is created. The idea is that you can utilize different models at different stages
for optimizing for quality and cost.

Moreover, it may be the case that user derives summary from files and database, and therefore, I explicitely added a summary to augment long form creation.

Note that Command R/R+ had 4k output window at the time of writing so, the max output variable is used to control Gemini, which had an 8k window.

Output length was kept same across the two for fairer comparison. 

The long form content is generated recursively, up to a limit of max_iterations current_iteration.

So, the maximum output token length would then be 4k * max_iterations, which has to be kept smaller than input token context (128k for Command R+ and 1 million+ for Gemini-1.5 at the time of writing)

While the generated content would not be good enough for a quality standalone creative work, it would surely expedite the creation of
such creative works by giving humans a broader canvas to play with.

I have also artificially added a 45 second delay prior to each generation to avoid hitting the free API rate limits because for this use case
latency isn't really a concern.
'''

import google.generativeai as genai
import cohere
import os
from dotenv import load_dotenv
from time import time, sleep

load_dotenv()

# Model configuration
max_tokens_per_generation=4096
max_iterations=15
temperature=0.75
research_instruction="""
1. Generate research material based on user's query for generating long form content. Your generated content would be used by another LLM to expand on your response.

2. Give a detailed response to the user's query. Give as many suggestions as you can.

3. If the user's requested content is a story, movie or a podcast, automatically create characters based on user's query, and narration's plot.
"""

long_form_content_instruction="""
1. Generate long form content based on user's query. Infer the type of long form content based on user's query.

2. If the user's requested content is a story, movie or a podcast, infer fictitious characters based on the research material. 

3. If the user's requested content is a story, movie or a podcast, strictly follow chapter/section titles and content as suggested by the research material.

4. Do not include any salutation message at the beginning of your response, directly generate the content. Do not include any closing message.

5. Always consider the entire input context which includes user's query and your response, that you have generated over multiple current_iteration.

6. Your task is to add to what you have already generated based on the user's query, in a coherent manner. 

7. The input will have the following format:

User Prompt: 

Research Material: 

AI Response generated so far:

8. Your response gets added to "AI Response generated so far".

9. Be as detailed as possible, and write in a tone based on user's requested content format, which could be story, article, podcast or movie script.

10. Include references and recollections from your previously generated responses in a coherent manner.

11. If the system instruction specifies that your response is the last iteration in iterative generation, then you must end the content with a closing message. This would be an ending context for a story, or closing messages in a podcast.
"""



# API configuration
genai.configure(api_key=os.getenv("GEMINI_KEY"))
co=cohere.ClientV2(os.getenv("COHERE_KEY"))

def generate_research_material_gemini(user_prompt: str) -> str:
    research_model=genai.GenerativeModel(
        model_name="gemini-1.5-pro-002",
        system_instruction=research_instruction,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens_per_generation,
            temperature=temperature
        )
        )
    
    return research_model.generate_content(user_prompt).text

def generate_research_material_cohere(user_prompt:str) -> str:
    research_model=co.chat(
        model="command-r-plus-08-2024",
        temperature=temperature,
        messages=[
            {
                "role":"system",
                "content":research_instruction
            },
            {
                "role":"user",
                "content":user_prompt
            }
        ]
    )
    return research_model.message.content[0].text

def generate_long_form_content_gemini(user_prompt:str, research_material:str, ai_response:str) -> str:
    for current_iteration in range(max_iterations):
        sleep(45) # to avoid hitting rate limits
        if current_iteration==max_iterations-1:
            last_iteration_instruction=long_form_content_instruction+"\n\n 10. This is the last iteration, include a coherent closing message in your response based on the content generated so far."
            gemini_model=genai.GenerativeModel(
                model_name="gemini-1.5-pro-002",  
                system_instruction=last_iteration_instruction,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens_per_generation,
                    temperature=temperature
                )
            )
            gemini_input=f"User Prompt:\n {user_prompt}\nResearch Material:\n {research_material}\nAI Response generated so far: "
            final_response_iteration= gemini_model.generate_content(gemini_input).text
            ai_response+="\n" + final_response_iteration
        else:
            gemini_model=genai.GenerativeModel(
                model_name="gemini-1.5-pro-002", 
                system_instruction=long_form_content_instruction,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens_per_generation,
                    temperature=temperature
                )
            )
            gemini_input=f"User Prompt:\n {user_prompt}\nResearch Material:\n {research_material}\nAI Response generated so far: {ai_response}"
            more_ai_response= gemini_model.generate_content(gemini_input).text
            ai_response+="\n" + more_ai_response
    
    return ai_response

def generate_long_form_content_cohere(user_prompt:str, research_material:str, ai_response:str) -> str:
    for current_iteration in range(max_iterations):
        sleep(45) # to avoid hitting rate limits
        if current_iteration==max_iterations-1:
            last_iteration_instruction=long_form_content_instruction+"\n\n 10. This is the last iteration, include a coherent closing message in your response based on the content generated so far."
            cohere_model=co.chat(
                model="command-r-plus-08-2024",
                temperature=temperature,
                messages=[
                    {
                        "role":"system",
                        "content":last_iteration_instruction
                    },
                    {
                        "role":"user",
                        "content":f"User Prompt:\n {user_prompt}\nResearch Material:\n {research_material}\nAI Response generated so far: {ai_response}"
                    }
                ]
            )
            final_response_iteration= cohere_model.message.content[0].text
            ai_response=ai_response+"\n" + final_response_iteration
        else:
            cohere_model=co.chat(
            model="command-r-plus-08-2024",
            temperature=temperature,
            messages=[
                {
                    "role":"system",
                    "content":long_form_content_instruction
                },
                {
                    "role":"user",
                    "content":f"User Prompt: {user_prompt}\nResearch Material: {research_material}\nAI Response generated so far: {ai_response}"
                }
            ]
            )
            more_ai_response= cohere_model.message.content[0].text
            ai_response=ai_response+"\n" + more_ai_response

    return ai_response

# Cohere generation
cohere_response=open("cohere_longform.txt","w")

user_prompt=input("What kind of long form content do you want to generate today?\n\n")
start_time=time()
research_response=generate_research_material_cohere(user_prompt=user_prompt)

cohere_response.write(f"User prompt:\n\n {user_prompt}\n]nResearch Material:\n\n {research_response}\n")

long_form_content=generate_long_form_content_cohere(user_prompt=user_prompt, research_material=research_response, ai_response="")
cohere_response.write(f"AI long form content generated: {long_form_content}")
end_time=time()
print(f"Total time taken to generate your content: {end_time-start_time} seconds")

# # Gemini generation
# gemini_response=open("gemini_longform.txt","w")

# user_prompt=input("What kind of long form content do you want to generate today?\n\n")
# start_time=time()
# research_response=generate_research_material_gemini(user_prompt=user_prompt)

# gemini_response.write(f"User prompt:\n\n {user_prompt}\n\nResearch Material:\n\n {research_response}\n\n")

# long_form_content=generate_long_form_content_gemini(user_prompt=user_prompt, research_material=research_response, ai_response="")
# gemini_response.write(f"AI long form content generated:\n\n {long_form_content}")
# end_time=time()
# print(f"Total time taken to generate your content: {end_time-start_time} seconds")