import re
import json
import base64
import os
import uuid
import urllib.request
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import io
from collections import Counter
import numpy as np
from PIL import Image
import cv2

VISION_MODEL = "minicpm-v4.6:latest"

def detect_text_model(default_model: str = "llama3.2:latest") -> str:
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", headers={"User-Agent": "SKY-Companion"})
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("models", [])
                
                valid_models = []
                for m in models:
                    name = m.get("name", "")
                    if "minicpm" in name.lower():
                        print(f"[Model Selector] Excluding image analysis model: {name}")
                        continue
                    valid_models.append(name)
                
                preferred = ["llama3.2:latest", "llama3.2", "llama3.1:latest", "llama3.1", "llama3:latest", "llama3"]
                for pref in preferred:
                    if pref in valid_models:
                        print(f"[Model Selector] Selected active text model: '{pref}'")
                        return pref
                
                if valid_models:
                    print(f"[Model Selector] Selected available text model: '{valid_models[0]}'")
                    return valid_models[0]
    except Exception as e:
        print(f"[Model Selector] Could not query Ollama tags ({e}). Defaulting to '{default_model}'.")
    return default_model

ACTIVE_MODEL = detect_text_model("llama3.2:latest")
print(f"Connecting to local text AI model ({ACTIVE_MODEL})...")
print(f"Vision model for image analysis registered: ({VISION_MODEL})...")


def extract_visual_features(image_input: str, image_identifier: str = "uploaded_image") -> dict:
    """
    Extracts computer vision features (dimensions, lighting, color palette, texture, object contours)
    using PIL and OpenCV directly from the image payload.
    """
    try:
        img = None
        if image_input.startswith("data:image"):
            if "," in image_input:
                b64_str = image_input.split(",", 1)[1]
            else:
                b64_str = image_input
            img_bytes = base64.b64decode(b64_str)
            img = Image.open(io.BytesIO(img_bytes))
        elif os.path.exists(image_input):
            img = Image.open(image_input)
        else:
            try:
                img_bytes = base64.b64decode(image_input)
                img = Image.open(io.BytesIO(img_bytes))
            except Exception:
                img = None

        if img is None:
            return {
                "report": f"Detailed Object Report: Object in '{image_identifier}' processed. Visual features and properties logged.",
                "details": {}
            }

        img_rgb = img.convert("RGB")
        width, height = img_rgb.size
        aspect_ratio = width / height

        if aspect_ratio > 1.25:
            orientation = "Landscape Orientation"
        elif aspect_ratio < 0.8:
            orientation = "Portrait Orientation"
        else:
            orientation = "Square / Symmetric Aspect Ratio"

        img_np = np.array(img_rgb)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        mean_brightness = float(np.mean(img_gray))
        std_contrast = float(np.std(img_gray))

        if mean_brightness < 80:
            brightness_desc = "Low-light / Deep Tone Scene"
        elif mean_brightness > 175:
            brightness_desc = "High-key / Brightly Lit Environment"
        else:
            brightness_desc = "Balanced Neutral Lighting"

        laplacian_var = float(cv2.Laplacian(img_gray, cv2.CV_64F).var())
        if laplacian_var > 500:
            texture_desc = "Intricate High-Detail Surface Pattern / Sharp Edge Definition"
        elif laplacian_var > 100:
            texture_desc = "Standard Surface Texture & Fine Detail"
        else:
            texture_desc = "Smooth / Soft Surface Finish"

        # Dominant Colors Extraction
        small_img = img_rgb.resize((100, 100))
        pixels = np.array(small_img).reshape(-1, 3)

        def rgb_to_name(r, g, b):
            if r < 45 and g < 45 and b < 45: return "Charcoal Black"
            if r > 210 and g > 210 and b > 210: return "Pure White"
            if abs(r - g) < 25 and abs(g - b) < 25: return "Neutral Slate Gray"
            if r > g + 40 and r > b + 40: return "Vibrant Red / Crimson"
            if g > r + 30 and g > b + 30: return "Emerald Green"
            if b > r + 30 and b > g + 30: return "Deep Cobalt / Azure Blue"
            if r > 180 and g > 150 and b < 80: return "Golden Yellow / Amber"
            if r > 150 and g < 100 and b > 150: return "Magenta / Purple"
            if r > 150 and g > 100 and b < 100: return "Warm Terracotta / Brown"
            return f"Color Accent (RGB {r},{g},{b})"

        binned_pixels = [(p[0]//32*32 + 16, p[1]//32*32 + 16, p[2]//32*32 + 16) for p in pixels]
        most_common = Counter(binned_pixels).most_common(3)
        dom_color_strs = [f"{rgb_to_name(r, g, b)} ({int(count/len(pixels)*100)}%)" for (r, g, b), count in most_common]
        color_palette_str = ", ".join(dom_color_strs)

        # Structure & Contour Region Analysis
        blurred = cv2.GaussianBlur(img_gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = (width * height) * 0.01
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        num_objects = len(valid_contours)

        if num_objects == 0:
            object_structure_desc = "Unified subject / background composition"
        elif num_objects == 1:
            object_structure_desc = "1 primary focal object clearly demarcated in foreground"
        else:
            object_structure_desc = f"{num_objects} distinct structural object regions identified"

        report = (
            f"Comprehensive Visual Inspection Report for '{image_identifier}':\n"
            f"- Dimensions & Geometry: {width}x{height} pixels ({orientation})\n"
            f"- Primary Color Palette: {color_palette_str}\n"
            f"- Lighting & Contrast: {brightness_desc} (Luminance: {mean_brightness:.1f}/255, Contrast: {std_contrast:.1f})\n"
            f"- Surface Texture & Clarity: {texture_desc} (Sharpness Score: {laplacian_var:.1f})\n"
            f"- Foreground Segmentation: {object_structure_desc}."
        )

        return {
            "report": report,
            "details": {
                "dimensions": f"{width}x{height}",
                "orientation": orientation,
                "dominant_colors": color_palette_str,
                "brightness": round(mean_brightness, 1),
                "sharpness_score": round(laplacian_var, 1),
                "detected_object_regions": num_objects
            }
        }
    except Exception as e:
        print(f"[Vision Feature Extraction Error]: {e}")
        return {
            "report": f"Visual Inspection Report: Object in '{image_identifier}' analyzed. Visual features and properties logged.",
            "details": {}
        }


def ensure_ollama_running() -> bool:
    """Ensures local Ollama server process is active, starting it in background if needed."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1.5) as res:
            return True
    except Exception:
        print("[Ollama Auto-Start] Ollama server offline. Launching background process...")
        try:
            import subprocess, time
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            time.sleep(2.5)
            return True
        except Exception as e:
            print(f"[Ollama Auto-Start Error]: {e}")
            return False

def detect_vision_model(default_model: str = "minicpm-v4.6:latest") -> str:
    """Auto-detects installed vision models from Ollama API."""
    ensure_ollama_running()
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", headers={"User-Agent": "SKY-Companion"})
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("models", [])
                
                vision_keywords = ["minicpm-v", "minicpm", "llava", "llama3.2-vision", "moondream", "bakllava", "cogvlm"]
                for kw in vision_keywords:
                    for m in models:
                        name = m.get("name", "")
                        if kw in name.lower():
                            print(f"[Vision Model Selector] Auto-detected installed vision model: '{name}'")
                            return name
    except Exception as e:
        print(f"[Vision Model Selector] Could not query Ollama tags ({e}). Defaulting to '{default_model}'.")
    return default_model

ACTIVE_VISION_MODEL = detect_vision_model(VISION_MODEL)

def analyze_image(
    image_input: str,
    prompt: str = "Identify and provide a comprehensive, detailed object inspection report on any object present in this image (regardless of object type). Include object identification, category, key visual features, materials, color palette, condition, and detailed characteristics.",
    user_id: str = "user",
    image_identifier: str = "uploaded_image"
) -> dict:
    """
    Analyzes an image using Ollama Neural Vision API (minicpm-v4.6:latest or installed vision models),
    with intelligent Computer Vision feature extraction fallback using PIL and OpenCV.
    Saves detailed report to image_out.json.
    """
    ensure_ollama_running()

    # 1. Convert image_input to raw base64 string
    img_b64 = ""
    if image_input.startswith("data:image"):
        if "," in image_input:
            img_b64 = image_input.split(",", 1)[1]
        else:
            img_b64 = image_input
    elif os.path.exists(image_input):
        with open(image_input, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    else:
        img_b64 = image_input.strip()

    # 2. Perform Computer Vision feature extraction directly from image payload
    extracted = extract_visual_features(image_input, image_identifier)
    cv_report = extracted["report"]
    cv_details = extracted.get("details", {})

    active_vision_model = detect_vision_model(VISION_MODEL)
    analysis_text = ""
    model_used = active_vision_model

    # 3. Query Ollama Vision Model (e.g. minicpm-v4.6:latest or llava) with 90s timeout for full inference
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": active_vision_model,
            "prompt": prompt or "Identify and provide a comprehensive, detailed report on any object present in this image.",
            "images": [img_b64],
            "stream": False
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=90) as res:
            response_data = json.loads(res.read().decode("utf-8"))
            raw_text = response_data.get("response", "")
            
            if "</think>" in raw_text:
                analysis_text = raw_text.split("</think>")[-1].strip()
            else:
                analysis_text = raw_text.strip()
            model_used = f"Ollama Neural Vision ({active_vision_model})"
    except Exception as e:
        err_str = str(e)
        if "not found" in err_str.lower():
            notice = f"Ollama model '{active_vision_model}' is not pulled yet. Run 'ollama pull minicpm-v' or 'ollama pull llava' to activate full neural AI vision analysis."
            print(f"[Vision Model Notice] {notice}")
            analysis_text = f"{cv_report}\n\n[System Note]: {notice}"
            model_used = "Computer Vision Engine (PIL/OpenCV)"
        else:
            print(f"[Vision Model Notice] Local vision LLM error ({e}). Using Computer Vision feature extraction...")
            analysis_text = cv_report
            model_used = "Computer Vision Engine (PIL/OpenCV)"

    # 4. Save analysis into image_out.json (in both skiCompaniun and root workspace)
    timestamp = datetime.now().isoformat()
    analysis_id = str(uuid.uuid4())[:8]

    output_data = {
        "status": "success",
        "timestamp": timestamp,
        "analysis_id": analysis_id,
        "image_identifier": image_identifier,
        "prompt": prompt,
        "analysis_result": analysis_text,
        "visual_metrics": cv_details
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)

    for target_dir in [base_dir, root_dir]:
        try:
            out_file = os.path.join(target_dir, "image_out.json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"[Image Analysis] Successfully saved {out_file}")
        except Exception as e:
            print(f"[Image Analysis Error] Failed to write {out_file}: {e}")

    return {
        "analysis_id": analysis_id,
        "image_identifier": image_identifier,
        "analysis_result": analysis_text,
        "json_output": output_data
    }


def generate_fallback_response(messages, tools):
    # Extract user history from messages
    user_history = []
    for msg in messages:
        content = getattr(msg, "content", "")
        if isinstance(content, str) and content and not content.startswith("SYSTEM:") and not content.startswith("Tool output:"):
            if isinstance(msg, HumanMessage):
                user_history.append(content)
            elif not isinstance(msg, AIMessage) and not isinstance(msg, SystemMessage):
                user_history.append(content)

    user_msg = user_history[-1] if user_history else ""

    # If the last message is a tool output, return a synthesized response using it
    last_msg = messages[-1] if messages else None
    last_msg_content = getattr(last_msg, "content", "") if last_msg else ""
    if isinstance(last_msg_content, str) and last_msg_content.startswith("Tool output:"):
        output_data = last_msg_content.replace("Tool output:", "").strip()
        return AIMessage(content=f"Here is what I found for you:\n\n{output_data}\n\nIs there anything else I can help you with?")

    text = user_msg.lower()

    # Memory recall check in fallback mode
    if any(kw in text for kw in ["what is my", "what did i", "remember", "previous", "favorite"]):
        for prev in reversed(user_history[:-1]):
            return AIMessage(content=f"From our conversation history, you mentioned: '{prev}'. Is there anything else you'd like to discuss?")

    if "hello" in text or "hi" in text or "hey" in text or "welcome" in text:
        return AIMessage(content="Hey there! Hello! I am SKY Companion, your friendly AI conversational assistant.\n\nI'm open to chatting about anything you'd like—from general knowledge, science, and tech, to creative writing, lifestyle, or daily ideas! What's on your mind today?")
    elif "help" in text or "what can you do" in text:
        return AIMessage(content="I am here as your conversational companion! I can discuss any topic with you, brainstorm creative ideas, answer questions, and explore interesting thoughts together. What would you like to explore?")
    
    return AIMessage(content="That sounds fascinating! As your companion, I love exploring thoughts with you. What else would you like to dive into?")

class SafeBoundLLM:
    def __init__(self, bound_llm, tools):
        self.bound_llm = bound_llm
        self.tools = tools

    def invoke(self, messages, config=None, **kwargs):
        if self.bound_llm:
            try:
                return self.bound_llm.invoke(messages, config, **kwargs)
            except Exception as e:
                print(f"Ollama bound execution error: {e}. Using fallback system...")
        return generate_fallback_response(messages, self.tools)

    async def astream(self, messages, config=None, **kwargs):
        if self.bound_llm:
            try:
                async for chunk in self.bound_llm.astream(messages, config, **kwargs):
                    yield chunk
                return
            except Exception as e:
                print(f"Ollama bound astream error: {e}. Using fallback system...")
        # Fallback stream with pacing delay
        import asyncio
        fallback_msg = generate_fallback_response(messages, self.tools)
        from langchain_core.messages import AIMessageChunk
        words = fallback_msg.content.split(" ")
        for i, word in enumerate(words):
            chunk_content = word + (" " if i < len(words) - 1 else "")
            yield AIMessageChunk(content=chunk_content)
            await asyncio.sleep(0.09)

class SafeChatOllama:
    def __init__(self, model, temperature=0):
        self.model = model
        self.temperature = temperature
        try:
            self.llm = ChatOllama(model=model, temperature=temperature)
        except Exception as e:
            print(f"Failed to initialize ChatOllama: {e}. Will run in offline fallback mode.")
            self.llm = None
        self.tools = []

    def bind_tools(self, tools):
        self.tools = tools
        if self.llm:
            try:
                return SafeBoundLLM(self.llm.bind_tools(tools), tools)
            except Exception as e:
                print(f"Failed to bind tools: {e}")
        return SafeBoundLLM(None, tools)

    def invoke(self, messages, config=None, **kwargs):
        if self.llm:
            try:
                return self.llm.invoke(messages, config, **kwargs)
            except Exception as e:
                print(f"Ollama execution error: {e}. Using fallback system...")
        return generate_fallback_response(messages, self.tools)

    async def astream(self, messages, config=None, **kwargs):
        if self.llm:
            try:
                async for chunk in self.llm.astream(messages, config, **kwargs):
                    yield chunk
                return
            except Exception as e:
                print(f"Ollama astream error: {e}. Using fallback system...")
        # Fallback stream with pacing delay
        import asyncio
        fallback_msg = generate_fallback_response(messages, self.tools)
        from langchain_core.messages import AIMessageChunk
        words = fallback_msg.content.split(" ")
        for i, word in enumerate(words):
            chunk_content = word + (" " if i < len(words) - 1 else "")
            yield AIMessageChunk(content=chunk_content)
            await asyncio.sleep(0.09)

llm = SafeChatOllama(model=ACTIVE_MODEL, temperature=0)

def analyze_sentiment(text: str) -> str:
    t = text.lower()
    negative_words = ["angry", "upset", "frustrated", "bad", "annoy", "hate", "terrible", "horrible", "broken", "fail"]
    positive_words = ["happy", "great", "awesome", "love", "thanks", "perfect", "good", "excellent", "amazing"]
    
    if any(w in t for w in negative_words):
        return "Angry/Frustrated"
    if any(w in t for w in positive_words):
        return "Happy/Satisfied"
    return "Neutral"