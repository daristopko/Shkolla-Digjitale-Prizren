import json
import random
from datetime import datetime
import config
from database import Strategy, Post, EngagementLog, init_db

DEFAULT_STRATEGY = {
    "niche": "software development",
    "brand_voice": "helpful, clear, and energetic",
    "target_audience": "developers, founders, and technical creators",
    "content_themes": "Python, automation, AI tools, developer productivity",
}

SUPPORTED_LANGUAGES = {
    "auto": "Auto-detect from topic and audience",
    "auto-detect from topic and audience": "Auto-detect from topic and audience",
    "english": "English",
    "albanian": "Albanian",
    "german": "German",
    "serbian": "Serbian",
}

BUSINESS_KNOWLEDGE_BASE = {
    "acoustic panels": {
        "positioning": "sound control products for offices, studios, hospitality, schools, and modern interiors",
        "angles": [
            "reduced echo and reverberation",
            "better speech privacy in open-plan offices",
            "interior design finishes that look architectural",
            "office fit-outs, meeting rooms, restaurants, studios, and home offices",
            "easy specification for architects, contractors, and facility managers",
        ],
        "visuals": "premium interior photo, acoustic wall panels, soft natural light, clean office or lounge, no clutter",
        "hashtags": ["#AcousticPanels", "#Soundproofing", "#InteriorDesign", "#OfficeFitOut", "#Architecture"],
    },
    "cyber security": {
        "positioning": "risk reduction, data protection, incident readiness, and trust for modern companies",
        "angles": [
            "practical protection against phishing and ransomware",
            "secure laptops, networks, cloud systems, and employee workflows",
            "trust, compliance, monitoring, and response time",
        ],
        "visuals": "professional cyber security analyst at a laptop with running security code, modern operations desk",
        "hashtags": ["#CyberSecurity", "#DataProtection", "#InfoSec", "#BusinessSecurity"],
    },
    "software development": {
        "positioning": "practical engineering education, automation, AI tooling, and developer productivity",
        "angles": [
            "clean code, maintainability, testing, automation, deployment, and workflow speed",
            "useful examples for developers, founders, and technical creators",
        ],
        "visuals": "minimal professional developer workspace with code on monitor, clean lighting",
        "hashtags": ["#SoftwareDevelopment", "#Python", "#Automation", "#DeveloperTips"],
    },
    "interior design": {
        "positioning": "beautiful, functional spaces for homes, offices, hospitality, and retail brands",
        "angles": [
            "materials, lighting, acoustics, layout, customer experience, and comfort",
            "before-after transformation value and practical specification tips",
        ],
        "visuals": "high-end interior photo, clean composition, natural materials, professional lighting",
        "hashtags": ["#InteriorDesign", "#DesignInspiration", "#CommercialInteriors", "#HomeDesign"],
    },
    "office fit-outs": {
        "positioning": "workspace planning, productivity, acoustics, brand experience, and employee comfort",
        "angles": [
            "meeting rooms, open-plan zones, quiet areas, acoustic comfort, furniture, and delivery timelines",
            "ROI through better focus, collaboration, and space efficiency",
        ],
        "visuals": "modern office fit-out with acoustic panels, workstations, meeting room glass, clean daylight",
        "hashtags": ["#OfficeFitOut", "#WorkspaceDesign", "#CommercialInteriors", "#WorkplaceStrategy"],
    },
}

class AIAgent:
    def __init__(self, db_session, active_account_id: str = "default"):
        init_db()
        self.db = db_session
        self.active_account_id = active_account_id or "default"
        self.api_key = config.OPENAI_API_KEY
        
        # Check if we should fall back to simulation mode
        self.is_simulated = (
            config.SIMULATION_MODE or 
            self.api_key == "YOUR_OPENAI_API_KEY" or 
            not self.api_key or 
            not self.api_key.startswith("sk-")
        )
        
        if not self.is_simulated:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            print("[AI Agent] Initialized Live OpenAI Client.")
        else:
            self.client = None
            print("[AI Agent] Initialized Simulated OpenAI Client.")

    def _get_strategy(self) -> Strategy:
        """Fetch the active brand strategy from the database."""
        strategy = (
            self.db.query(Strategy)
            .filter(Strategy.account_id == self.active_account_id)
            .order_by(Strategy.id.asc())
            .first()
        )
        if not strategy:
            strategy = Strategy(account_id=self.active_account_id)
            self.db.add(strategy)
            self.db.commit()
            self.db.refresh(strategy)
        return strategy

    def _strategy_value(self, strategy: Strategy, field: str) -> str:
        value = getattr(strategy, field, None)
        return value or DEFAULT_STRATEGY[field]

    def _resolve_language(self, language: str = None) -> str:
        """Upgrade: normalize requested output language while keeping auto mode available."""
        requested = (language or "English").strip().lower()
        return SUPPORTED_LANGUAGES.get(requested, language or "English")

    def _business_context(self, niche: str, topic: str = "") -> dict:
        """Upgrade: provide niche-specific business context for stronger B2B/B2C posts."""
        search_text = f"{niche} {topic}".lower()
        for key, details in BUSINESS_KNOWLEDGE_BASE.items():
            if key in search_text:
                return {"name": key, **details}
        return {
            "name": niche,
            "positioning": (
                "a practical business offering with a clear customer problem, measurable value, "
                "trust signals, use cases, objections, and a simple call to action"
            ),
            "angles": [
                "customer pain point and outcome",
                "why the solution matters now",
                "proof, process, comparison, care tips, buying criteria, and ROI",
            ],
            "visuals": f"professional photo directly illustrating {topic or niche}, simple composition, premium brand quality",
            "hashtags": [
                f"#{''.join(part.title() for part in niche.split())}",
                "#BusinessGrowth",
                "#SmallBusiness",
                "#B2B",
                "#Marketing",
            ],
        }

    def _language_templates(self, language_name: str) -> dict:
        """Upgrade: localized simulation templates for offline/demo generation."""
        templates = {
            "albanian": {
                "hook": "Nje ide e thjeshte per",
                "value": "Kur mesazhi eshte i qarte, klientet e kuptojne me shpejt vleren dhe marrin vendime me te sigurta.",
                "cta": "Ruaje kete postim dhe na shkruaj per nje rekomandim praktik.",
            },
            "german": {
                "hook": "Ein klarer Impuls fuer",
                "value": "Wenn Nutzen, Anwendung und Ergebnis sofort erkennbar sind, wirkt dein Angebot professioneller und vertrauenswuerdiger.",
                "cta": "Speichere diesen Beitrag und schreibe uns, wenn du eine konkrete Empfehlung brauchst.",
            },
            "serbian": {
                "hook": "Jednostavna ideja za",
                "value": "Kada su problem, resenje i rezultat jasni, kupci brze razumeju vrednost i lakse donose odluku.",
                "cta": "Sacuvaj ovu objavu i pisi nam za praktican predlog.",
            },
        }
        return templates.get(language_name.lower(), {
            "hook": "A simple business insight for",
            "value": "When the problem, solution, and outcome are clear, customers understand the value faster and trust the offer more.",
            "cta": "Save this post and message us if you want a practical recommendation.",
        })

    def _simulate_caption(self, topic: str, niche: str, language_name: str, context: dict) -> dict:
        """Upgrade: niche-aware fallback that mirrors the live JSON contract."""
        tpl = self._language_templates(language_name)
        angle = random.choice(context["angles"])
        image_style = random.choice(["text", "photo"])
        caption = (
            f"{tpl['hook']} {topic}.\n\n"
            f"{tpl['value']}\n\n"
            f"Focus: {angle}.\n\n"
            f"{tpl['cta']}"
        )
        hashtags = " ".join((context.get("hashtags") or [])[:5])
        if not hashtags:
            hashtags = f"#{niche.replace(' ', '')} #Business #InstagramMarketing"
        if image_style == "text":
            media_prompt = (
                f"Exceptionally simple premium Instagram typography card about {topic}; "
                f"medium-sized eye-catching headline, lots of negative space, clean contrast, professional layout."
            )
        else:
            media_prompt = (
                f"{context['visuals']}; high-quality professional photo, simple direct subject, realistic lighting, no text."
            )
        return {
            "caption": caption,
            "hashtags": hashtags,
            "media_prompt": media_prompt,
            "language": language_name,
            "image_style": image_style,
        }

    def generate_caption(self, topic: str = None, language: str = "English") -> dict:
        """Generates a localized caption, hashtags, and professional media prompt."""
        strategy = self._get_strategy()

        niche = self._strategy_value(strategy, "niche")
        voice = self._strategy_value(strategy, "brand_voice")
        audience = self._strategy_value(strategy, "target_audience")
        themes = self._strategy_value(strategy, "content_themes")
        language_name = self._resolve_language(language)

        if not topic:
            topics = [t.strip() for t in themes.split(",")]
            topic = random.choice(topics) if topics else "general business tips"

        context = self._business_context(niche, topic)
        prompt_topic = f"Topic: {topic} in the context of the {niche} niche"

        if self.is_simulated:
            return self._simulate_caption(topic, niche, language_name, context)

        try:
            system_prompt = (
                f"You are a professional social media manager and AI agent specializing in the '{niche}' niche. "
                f"Your brand voice is '{voice}'. The target audience is '{audience}'. "
                f"Write the entire caption and hashtags in {language_name}. "
                f"Use this business knowledge: positioning={context['positioning']}; content angles={context['angles']}. "
                f"Create a high-performing Instagram post. Output raw JSON ONLY with keys "
                f"'caption', 'hashtags', 'media_prompt', 'language', and 'image_style'. "
                f"Do not write markdown backticks or any other text before/after the JSON. Just raw JSON."
            )

            user_prompt = (
                f"Generate a post about: '{prompt_topic}'.\n"
                f"The 'caption' should be engaging, specific, useful, and fit the brand voice. "
                f"The 'hashtags' should be relevant, localized where natural, and formatted as a single string. "
                f"Set 'image_style' to either 'text' or 'photo'. Use 'text' for a simple typography image with "
                f"medium-sized eye-catching text, and 'photo' for purely visual content. "
                f"The 'media_prompt' must be highly professional and exceptionally simple. If image_style='photo', "
                f"describe a high-quality realistic photo that directly illustrates the topic, with no text in the image. "
                f"If image_style='text', describe a minimal premium layout with a short headline and lots of negative space. "
                f"Suggested visual direction: {context['visuals']}."
            )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            return {
                "caption": data.get("caption", ""),
                "hashtags": data.get("hashtags", ""),
                "media_prompt": data.get("media_prompt", ""),
                "language": data.get("language", language_name),
                "image_style": data.get("image_style", "text"),
            }
        except Exception as e:
            print(f"[AI Agent] OpenAI generation failed, falling back to simulated templates. Error: {e}")
            return self._simulate_caption(topic, niche, language_name, context)

    def _legacy_generate_caption(self, topic: str = None) -> dict:
        """Generates a caption, hashtags, and media asset prompt based on the brand voice/niche."""
        strategy = self._get_strategy()
        
        niche = self._strategy_value(strategy, "niche")
        voice = self._strategy_value(strategy, "brand_voice")
        audience = self._strategy_value(strategy, "target_audience")
        themes = self._strategy_value(strategy, "content_themes")
        
        if not topic:
            topics = [t.strip() for t in themes.split(",")]
            topic = random.choice(topics) if topics else "general tech tips"
            
        prompt_topic = f"Topic: {topic} in the context of the {niche} niche"

        if self.is_simulated:
            # Generate highly realistic templates based on niche
            mock_captions = [
                {
                    "caption": f"💡 Quick tips for mastering {topic}! When developing, keeping your design patterns clean is key. Here's a brief breakdown on how to apply this in your daily workflow.\n\nWhat are your thoughts on this approach? Let's discuss in the comments! 👇",
                    "hashtags": f"#{niche.replace(' ', '')} #Coding #Python #DeveloperLife #TechAgent",
                    "media_prompt": f"A clean, minimalist workspace layout with code showing on a monitor, neon violet accent lighting, high quality photography."
                },
                {
                    "caption": f"Unlocking productivity in {niche}: Focus on automation. 🤖 Today we are exploring how {topic} helps automate complex steps. This will save hours of manual setup.\n\nSave this post for later reference! 💾",
                    "hashtags": f"#{niche.replace(' ', '')} #DeveloperCommunity #Automation #SoftwareEngineering",
                    "media_prompt": f"A stylized 3D render of an abstract computer processor unit glowing with cyan light, isometric view, sleek tech style."
                },
                {
                    "caption": f"A developer's checklist for {topic}. 📝\n1️⃣ Keep it modular\n2️⃣ Document the interfaces\n3️⃣ Test the happy path and edge cases.\n\nWhich step do programmers overlook the most? Share below!",
                    "hashtags": f"#{niche.replace(' ', '')} #CleanCode #TipsAndTricks #CodeNewbie",
                    "media_prompt": f"Dark theme background with checklist checkboxes glowing violet, flat vector style, ultra modern UI."
                }
            ]
            return random.choice(mock_captions)
        
        try:
            system_prompt = (
                f"You are a professional social media manager and AI agent specializing in the '{niche}' niche. "
                f"Your brand voice is '{voice}'. The target audience is '{audience}'. "
                f"Create a high-performing Instagram post. Output raw JSON ONLY with keys 'caption', 'hashtags', and 'media_prompt'. "
                f"Do not write markdown backticks or any other text before/after the JSON. Just raw JSON."
            )
            
            user_prompt = (
                f"Generate a post about: '{prompt_topic}'.\n"
                f"The 'caption' should be engaging and fit the brand voice. "
                f"The 'hashtags' should be relevant and formatted as a single string. "
                f"The 'media_prompt' should describe a visually stunning image or layout that matches the post context."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            return {
                "caption": data.get("caption", ""),
                "hashtags": data.get("hashtags", ""),
                "media_prompt": data.get("media_prompt", "")
            }
        except Exception as e:
            print(f"[AI Agent] OpenAI generation failed, falling back to simulated templates. Error: {e}")
            # Quick fallback template
            return {
                "caption": f"Developing skills in {niche} around {topic}! It's a continuous journey of learning and optimizing. 🚀",
                "hashtags": f"#{niche.replace(' ', '')} #TechTips",
                "media_prompt": "Minimalist tech workspace with neon lighting."
            }

    def generate_comment_reply(self, comment_text: str, commenter_username: str) -> str:
        """Generates a contextual reply to an Instagram comment using LLM/heuristics."""
        strategy = self._get_strategy()
        niche = self._strategy_value(strategy, "niche")
        voice = self._strategy_value(strategy, "brand_voice")
        
        if self.is_simulated:
            comment_lower = comment_text.lower()
            if "why" in comment_lower or "how" in comment_lower:
                return f"@{commenter_username} That's a great question! It helps prevent memory leaks and isolates namespaces so variables don't conflict. 💡"
            if "great" in comment_lower or "nice" in comment_lower or "love" in comment_lower:
                return f"@{commenter_username} Thanks! Glad you enjoyed the content. Stay tuned for more code snippets! 🙌"
            return f"@{commenter_username} Absolutely! Thanks for dropping by. Let me know if you have any other questions about {niche}!"
            
        try:
            system_prompt = (
                f"You are the AI manager of an Instagram page in the '{niche}' niche. "
                f"Your brand voice is '{voice}'. "
                f"Write a short, engaging, and friendly reply (maximum 2 sentences) to the user's comment. "
                f"Always tag them with their username @{commenter_username} at the start."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User '{commenter_username}' commented: '{comment_text}'"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI Agent] OpenAI comment reply generation failed. Error: {e}")
            return f"@{commenter_username} Thanks for the feedback! 🚀"

    def generate_dm_reply(self, message_text: str, user_username: str) -> str:
        """Generates a conversational DM response to nurture followers."""
        strategy = self._get_strategy()
        niche = self._strategy_value(strategy, "niche")
        voice = self._strategy_value(strategy, "brand_voice")
        
        if self.is_simulated:
            msg_lower = message_text.lower()
            if "fastapi" in msg_lower:
                return f"Hi @{user_username}! FastAPI is amazing. I suggest reading their official documentation, which is fantastic, and starting with a basic CRUD API using SQLAlchemy."
            if "clean code" in msg_lower:
                return f"Hey @{user_username}, clean code is super critical! Keeping functions small and naming variables clearly are great starting points. Check out the book 'Clean Code' by Uncle Bob."
            if "hello" in msg_lower or "hey" in msg_lower or "hi" in msg_lower:
                return f"Hello @{user_username}! I'm an autonomous agent managing this page. How can I help you today with learning {niche}?"
            return f"Hey @{user_username}! Thanks for reaching out. In our {niche} page, we try to focus on modern development tips. Do you have any topics you'd like us to cover next?"
            
        try:
            system_prompt = (
                f"You are an AI assistant managing the Direct Messages for an Instagram account in the '{niche}' niche. "
                f"Your voice is '{voice}'. Have a natural, helpful, human-like chat conversation. "
                f"Answer the user's message concisely. Do not sound too formal; maintain a helpful and personal vibe."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User '{user_username}' sent a DM: '{message_text}'"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI Agent] OpenAI DM reply generation failed. Error: {e}")
            return f"Hi @{user_username}! Thanks for reaching out. I'll make sure the human creator reviews this as soon as possible. Let me know if there's anything else!"

    def get_content_strategy_suggestions(self) -> list:
        """Suggests 3 ideas for upcoming content based on niche & voice settings."""
        strategy = self._get_strategy()
        niche = self._strategy_value(strategy, "niche")
        context = self._business_context(niche)
        
        if self.is_simulated:
            angles = context["angles"]
            return [
                {
                    "title": f"Common buying mistakes in {niche}",
                    "description": f"A carousel explaining what customers should check before choosing a provider, including {angles[0]}.",
                    "estimated_engagement": "High (Sharable content)"
                },
                {
                    "title": f"Before and after: {niche} results",
                    "description": "A simple visual post that shows the customer problem, the solution, and the practical business outcome.",
                    "estimated_engagement": "Very High (Saves and comments)"
                },
                {
                    "title": f"How to choose the right {niche} solution",
                    "description": f"A practical checklist for prospects covering {angles[-1]}, budget, quality, and implementation.",
                    "estimated_engagement": "High (Saves)"
                }
            ]
            
        try:
            system_prompt = (
                f"You are a Content Strategy Consultant for a social media page in the '{niche}' niche. "
                f"Use this business context: positioning={context['positioning']}; angles={context['angles']}. "
                f"Provide exactly 3 upcoming post ideas in JSON array format. "
                f"Each idea object must contain keys: 'title', 'description', and 'estimated_engagement'. "
                f"Output raw JSON only. Do not wrap in markdown backticks."
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Suggest three future content ideas."}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            # Handle if the model returned { "ideas": [...] }
            if "ideas" in data:
                return data["ideas"]
            elif isinstance(data, list):
                return data
            else:
                # If it's a dict containing the elements directly
                items = []
                for key, val in data.items():
                    if isinstance(val, list):
                        return val
                return [data]
        except Exception as e:
            print(f"[AI Agent] OpenAI content strategy failed. Error: {e}")
            return [
                {"title": f"Introduction to {niche}", "description": "Fundamentals guide", "estimated_engagement": "Medium"}
            ]


def generate_caption_and_hashtags(strategy: Strategy, topic: str, language: str = "English") -> dict:
    """Upgrade: compatibility wrapper for the Tk desktop app's older import path."""
    agent = object.__new__(AIAgent)
    niche = getattr(strategy, "niche", None) or DEFAULT_STRATEGY["niche"]
    language_name = agent._resolve_language(language)
    context = agent._business_context(niche, topic)
    return agent._simulate_caption(topic, niche, language_name, context)


def generate_comment_reply(strategy: Strategy, comment_text: str, commenter_username: str) -> str:
    """Compatibility wrapper for desktop_app.py comment replies."""
    niche = getattr(strategy, "niche", None) or DEFAULT_STRATEGY["niche"]
    comment_lower = (comment_text or "").lower()
    if "price" in comment_lower or "cost" in comment_lower:
        return f"@{commenter_username} Thanks for asking. Pricing depends on the project scope, so message us a few details and we can guide you."
    if "how" in comment_lower or "why" in comment_lower:
        return f"@{commenter_username} Great question. For {niche}, the best answer depends on the space, goal, and customer need."
    return f"@{commenter_username} Thanks for your comment. We are happy to help with anything around {niche}."


def generate_dm_reply(strategy: Strategy, message_text: str, user_username: str) -> str:
    """Compatibility wrapper for desktop_app.py DM replies."""
    niche = getattr(strategy, "niche", None) or DEFAULT_STRATEGY["niche"]
    msg_lower = (message_text or "").lower()
    if "price" in msg_lower or "quote" in msg_lower or "cost" in msg_lower:
        return f"Hi @{user_username}, thanks for reaching out. Send us the project size, location, and goal, and we can suggest the right next step for {niche}."
    return f"Hi @{user_username}, thanks for messaging us. Tell us what you want to improve, and we will point you toward the best {niche} option."
