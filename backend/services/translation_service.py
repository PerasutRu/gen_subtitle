import os
from pathlib import Path
from openai import OpenAI
from typing import List, Optional
import asyncio
from services.transcription_service import TranscriptionService
from models.subtitle_models import SubtitleSegment

class TranslationService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        self.transcription_service = TranscriptionService()
        
        self.language_map = {
            "english": "อังกฤษ",
            "lao": "ลาว", 
            "myanmar": "พม่า",
            "khmer": "กัมพูชา",
            "vietnamese": "เวียดนาม"
        }
    
    async def translate_srt(self, srt_path: Path, target_language: str, style_prompt: Optional[str] = None) -> str:
        """แปลไฟล์ SRT เป็นภาษาเป้าหมาย"""
        try:
            # Parse SRT file
            segments = self.transcription_service.parse_srt_file(srt_path)
            
            # Translate segments
            translated_segments = await self._translate_segments(segments, target_language, style_prompt)
            
            # Generate SRT content
            return self.transcription_service._generate_srt_content(translated_segments)
            
        except Exception as e:
            raise Exception(f"การแปลล้มเหลว: {str(e)}")
    
    async def _translate_segments(self, segments: List[SubtitleSegment], target_language: str, style_prompt: Optional[str] = None) -> List[SubtitleSegment]:
        """แปลแต่ละ segment"""
        translated_segments = []
        
        # Prepare texts for batch translation
        texts_to_translate = [segment.text for segment in segments]
        
        # Create translation prompt
        system_prompt = self._create_translation_prompt(target_language, style_prompt)
        
        # Batch translate (process in chunks to avoid token limits)
        chunk_size = 10
        for i in range(0, len(texts_to_translate), chunk_size):
            chunk_texts = texts_to_translate[i:i + chunk_size]
            chunk_segments = segments[i:i + chunk_size]
            
            translated_chunk = await self._translate_text_batch(chunk_texts, system_prompt)
            
            # Create translated segments
            for j, translated_text in enumerate(translated_chunk):
                original_segment = chunk_segments[j]
                translated_segments.append(SubtitleSegment(
                    start=original_segment.start,
                    end=original_segment.end,
                    text=translated_text.strip()
                ))
        
        return translated_segments
    
    def _create_translation_prompt(self, target_language: str, style_prompt: Optional[str] = None) -> str:
        """สร้าง prompt สำหรับการแปล"""
        language_name = self.language_map.get(target_language, target_language)
        
        base_prompt = f"""คุณเป็นนักแปลมืออาชีพ กรุณาแปลข้อความต่อไปนี้จากภาษาไทยเป็นภาษา{language_name}

คำแนะนำ:
1. รักษาความยาวของข้อความให้ใกล้เคียงกับต้นฉบับ
2. แปลให้เป็นธรรมชาติและเข้าใจง่าย
3. รักษาความหมายและบริบทเดิม
4. ใช้คำศัพท์ที่เหมาะสมกับเนื้อหา"""

        if style_prompt:
            base_prompt += f"\n5. สไตล์การแปล: {style_prompt}"
        
        base_prompt += "\n\nกรุณาแปลข้อความแต่ละบรรทัดและตอบกลับในรูปแบบเดียวกัน (แต่ละบรรทัดแยกด้วย newline)"
        
        return base_prompt
    
    async def _translate_text_batch(self, texts: List[str], system_prompt: str) -> List[str]:
        """แปลข้อความเป็นชุด"""
        try:
            # Join texts with special separator
            input_text = "\n---SEPARATOR---\n".join(texts)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": input_text}
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
            )
            
            translated_text = response.choices[0].message.content
            
            # Split back into individual translations
            translated_texts = translated_text.split("\n---SEPARATOR---\n")
            
            # Ensure we have the same number of translations
            if len(translated_texts) != len(texts):
                # Fallback: translate one by one
                return await self._translate_texts_individually(texts, system_prompt)
            
            return translated_texts
            
        except Exception as e:
            # Fallback: translate one by one
            return await self._translate_texts_individually(texts, system_prompt)
    
    async def _translate_texts_individually(self, texts: List[str], system_prompt: str) -> List[str]:
        """แปลข้อความทีละข้อ (fallback method)"""
        translated_texts = []
        
        for text in texts:
            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                )
                
                translated_text = response.choices[0].message.content.strip()
                translated_texts.append(translated_text)
                
            except Exception as e:
                # If translation fails, keep original text
                translated_texts.append(text)
        
        return translated_texts