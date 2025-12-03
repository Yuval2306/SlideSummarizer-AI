import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def create_explanation_prompt(slide_text):
    """Create a shorter prompt for Gemini API based on slide text."""
    prompt = f"Explain this PowerPoint slide text clearly and concisely: {slide_text}"
    return prompt


async def get_explanation(slide_text, timeout=30):
    """Get an explanation for a slide from Gemini API."""
    try:
        prompt = await create_explanation_prompt(slide_text)

        model = genai.GenerativeModel('models/gemini-1.5-flash')  # Instead of 'gemini-1.5-pro'

        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=timeout
        )

        return response.text

    except asyncio.TimeoutError:
        return "Error: The request to Gemini API timed out."
    except Exception as e:
        return f"Error explaining this slide: {str(e)}"


async def process_slides(slides, delay_seconds=3, max_parallel=3):
    """Process slides asynchronously with rate limiting to avoid quota issues."""
    results = []

    for i in range(0, len(slides), max_parallel):
        batch = slides[i:i + max_parallel]
        tasks = []

        for slide in batch:
            task = asyncio.create_task(get_explanation(slide["text"]))
            tasks.append((slide["slide_number"], task))

        for slide_number, task in tasks:
            try:
                explanation = await task
                results.append({
                    "slide_number": slide_number,
                    "explanation": explanation
                })
            except Exception as e:
                results.append({
                    "slide_number": slide_number,
                    "explanation": f"Error processing slide {slide_number}: {str(e)}"
                })

        if i + max_parallel < len(slides):
            print(f"Waiting {delay_seconds} seconds before processing next batch...")
            await asyncio.sleep(delay_seconds)

    results.sort(key=lambda x: x["slide_number"])
    return results