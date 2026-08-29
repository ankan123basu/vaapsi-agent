import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

async def main():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
    )
    try:
        res = await llm.ainvoke("Respond with JSON: {\"status\": \"ok\"}")
        print("MODEL: gemini-2.5-flash SUCCESS!")
        print("CONTENT TYPE:", type(res.content))
        print("CONTENT:", repr(res.content))
    except Exception as e:
        print("gemini-2.5-flash failed:", e)

    llm2 = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
    )
    try:
        res2 = await llm2.ainvoke("Respond with JSON: {\"status\": \"ok\"}")
        print("MODEL: gemini-2.0-flash-exp SUCCESS!")
        print("CONTENT TYPE:", type(res2.content))
        print("CONTENT:", repr(res2.content))
    except Exception as e:
        print("gemini-2.0-flash-exp failed:", e)

if __name__ == "__main__":
    asyncio.run(main())
