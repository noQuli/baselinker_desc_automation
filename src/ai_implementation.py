import os
import asyncio
from typing import Tuple
from pydantic import BaseModel, Field
from langchain_perplexity import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import aiohttp
from src.logger import SingletonLogger
from dotenv import load_dotenv
import hashlib
import json

load_dotenv()

logger = SingletonLogger().get_logger()

PROMPT_TEMPLATE = """
Stwórz dokładny i atrakcyjny zgodny z zasadami gramatyki i stylistyki w języku polskim, opis produktu na aukcję Allegro, zgodny z danymi przesłanymi niżej,
który zaraz wyślę Wymagania: SEO i sprzedaż – zoptymalizowany pod Allegro,
czytelny i przyciągający uwagę. Struktura: Opis produktu – nagłówek H1,
większa czcionka, pogrubione tytuły sekcji. Kluczowe cechy – uwzględnij wszystkie dane,
uyj pogrubień dla istotnych informacji. Użyj tego emotka ✅ przy wymienianiu.
Specyfikacja techniczna – nagłówek H2, dokładne tłumaczenie, zachowanie oryginalnych wartości
i terminologii, ale wypunktowane kropkami, pilnuj aby zawsze były wymiary podzielone na wysokość,
szerokość, długość Zastosowanie – nagłówek H1 konkretne przykłady użycia,
jakie problemy rozwiązuje produkt. Użyj tego emotka ⭐ przy wymienianiu.
Zawartość zestawu –nagłówek H1 tłumaczenie, pełna lista elementów. Korzyści z zakupu
–nagłówek H1 podkreślenie korzyści, które płyną z posiadania tego produktu Użyj tego emotka
➡️przy wymienianiu. Dlaczego warto wybrać ten produkt? – chwytliwe zwroty, wezwanie do działania.
zapisane w formacie h2 Dodatkowe wytyczne: Bez nazwy producenta Vevor, nr modelu w specyfikacji
Frazy kluczowe zwiększające widoczność w wyszukiwarce. Używaj tylko Polskich jednostek,
zamieniaj jednostki na polskie Formatowanie – nagłówki, akapity, listy punktowane Emocjonalny język
i chwytliwe zwroty dla większej konwersji. Napisz to w html, zważając na nagłówki i pogrubienia nie
używaj słów nasza, nasze, ta, ten, bo jako rozpoczęcie zdania nagłówki pisz tylko pierwsze słowo z
dużej litery Cel: Gotowy opis, zgodny z danymi, atrakcyjny i zoptymalizowany pod sprzedaż.
Pisz tylko potrzebny tekst, nie dodawaj oznaczenie ze to jest html.  
Rozdziel kod opisu i kod korzyści z zakupu słowem: ROZDZIEL.  
---
{description}
"""

BENEFITS_SEPARATOR = "ROZDZIEL"
DEFAULT_MODEL_NAME = "sonar"

CACHE = {}

class GeneratedDescription(BaseModel):
    description: str = Field(..., description="The main part of the product description.")
    benefits: str = Field(..., description="The section describing the benefits of the purchase.")

class ProductDescriptionGenerator:
    def __init__(self, description: str, model_name: str = DEFAULT_MODEL_NAME):
        self.api_key = os.getenv("PPLX_API_KEY")
        self.model_name = model_name
        self.description = description
        self.chain = self._init_chain()

    def _split_response(self, response: str) -> Tuple[str, str]:
        try:
            parts = response.split(BENEFITS_SEPARATOR)
            if len(parts) == 2:
                description_part = parts[0]
                benefits_part = parts[1]
                return description_part, benefits_part
            else:
                logger.warning("Response did not split cleanly, returning full response as description")
                return response, ""
        except Exception as e:
            logger.error(f"Could not split response: {e}")
            return response, ""

    def _init_chain(self):
        try:
            chain = (
                ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
                | ChatPerplexity(pplx_api_key=self.api_key, model=self.model_name)
                | StrOutputParser()
            )
            logger.debug("Successfully initialized chain")
            return chain
        except Exception as e:
            logger.error(f"Could not initialize model chain: {e}")

    async def generate_async(self) -> GeneratedDescription:
        description_hash = hashlib.sha256(self.description.encode()).hexdigest()
        if description_hash in CACHE:
            logger.info("Using cached response")
            cached_response = CACHE[description_hash]
        else:
            loop = asyncio.get_event_loop()
            try:
                response = await loop.run_in_executor(None, self.chain.invoke, {"description": self.description})
                CACHE[description_hash] = response
                cached_response = response
                logger.info("Generated response and cached it")
            except Exception as e:
                logger.error(f"Error during generation: {e}")
                cached_response = ""

        description_part, benefits_part = self._split_response(cached_response)
        return GeneratedDescription(description=description_part, benefits=benefits_part)

    def generate(self) -> GeneratedDescription:
        return asyncio.run(self.generate_async())
