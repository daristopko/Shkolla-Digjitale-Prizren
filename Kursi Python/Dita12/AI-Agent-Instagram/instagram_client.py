import os
import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import config

class InstagramClientInterface:
    """Interface to define standard methods for real and simulated Instagram interactions."""
    def login(self) -> bool:
        raise NotImplementedError
        
    def get_profile_info(self) -> dict:
        raise NotImplementedError
        
    def post_photo(self, image_path: str, caption: str) -> str:
        raise NotImplementedError
        
    def post_reel(self, video_path: str, caption: str) -> str:
        raise NotImplementedError
        
    def get_direct_messages(self) -> list:
        raise NotImplementedError
        
    def reply_to_direct_message(self, thread_id: str, text: str) -> bool:
        raise NotImplementedError
        
    def get_comments(self, media_id: str) -> list:
        raise NotImplementedError
        
    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        raise NotImplementedError
        
    def get_recent_posts(self, limit: int = 5) -> list:
        raise NotImplementedError


class MockInstagramClient(InstagramClientInterface):
    """Fully functional simulated Instagram client that operates on local storage and mock APIs."""
    
    def __init__(self, username="simulated_agent"):
        self.username = username
        self.logged_in = True
        
        # In-memory storage for simulated database interactions
        self.follower_count = 1358
        self.following_count = 482
        self.posts_count = 38
        
        # Load or generate mock posts
        self.mock_posts = [
            {
                "id": "mock_post_101",
                "caption": "Mastering Python Generators! ⚡️ If you are dealing with large datasets, generators help save memory by yielding elements one by one. Check the code outline! #Python #SoftwareEngineering #Performance",
                "like_count": 142,
                "comment_count": 6,
                "media_type": "image",
                "thumbnail_url": "https://picsum.photos/id/1/800/800",
                "taken_at": (datetime.utcnow() - timedelta(hours=18)).isoformat()
            },
            {
                "id": "mock_post_102",
                "caption": "Why clean code matters. 🧼 Writing readable code is a love letter to your future self and teammates. What are your core clean code principles? #Programming #CleanCode #DevLife",
                "like_count": 210,
                "comment_count": 12,
                "media_type": "image",
                "thumbnail_url": "https://picsum.photos/id/60/800/800",
                "taken_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
            },
            {
                "id": "mock_post_103",
                "caption": "Open Source contribution guide! 🌐 Ever wanted to contribute to GitHub but felt intimidated? Start small: improve docs, fix typos, then build up to code. #OpenSource #GitHub #TechTips",
                "like_count": 98,
                "comment_count": 3,
                "media_type": "image",
                "thumbnail_url": "https://picsum.photos/id/180/800/800",
                "taken_at": (datetime.utcnow() - timedelta(days=4)).isoformat()
            }
        ]
        
        # Load or generate mock DMs
        self.mock_dms = [
            {
                "id": "dm_thread_1",
                "username": "alex_coder",
                "text": "Hey! Do you have a recommended roadmap for learning FastAPI in 2026?",
                "timestamp": (datetime.utcnow() - timedelta(minutes=45)).isoformat(),
                "is_unread": True
            },
            {
                "id": "dm_thread_2",
                "username": "sara_designs",
                "text": "Absolutely love your post about clean code. Shared it with my team!",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "is_unread": True
            },
            {
                "id": "dm_thread_3",
                "username": "hardware_geek",
                "text": "Do you prefer Mac, Linux, or Windows for programming?",
                "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                "is_unread": False
            }
        ]
        
        # Load or generate mock comments
        self.mock_comments = {
            "mock_post_101": [
                {"id": "comm_1", "username": "py_guru", "text": "Generators are great! yield from is also super useful.", "is_unread": True},
                {"id": "comm_2", "username": "novice_dev", "text": "Does this work in Python 2 as well?", "is_unread": True}
            ],
            "mock_post_102": [
                {"id": "comm_3", "username": "architect_bob", "text": "Clean code is good, but don't over-engineer it early on.", "is_unread": False}
            ],
            "mock_post_103": []
        }

    def login(self) -> bool:
        print(f"[Simulated Client] Logging in as {self.username}...")
        self.logged_in = True
        return True
        
    def get_profile_info(self) -> dict:
        return {
            "username": self.username,
            "followers": self.follower_count,
            "following": self.following_count,
            "posts_count": self.posts_count,
            "full_name": "Autonomous Python AI Agent",
            "biography": "Leveraging generative AI to schedule code tutorials, tips, and auto-engage."
        }
        
    def post_photo(self, image_path: str, caption: str) -> str:
        print(f"[Simulated Client] Uploading photo '{image_path}' with caption: '{caption}'")
        self.posts_count += 1
        new_post_id = f"mock_post_{random.randint(200, 999)}"
        new_post = {
            "id": new_post_id,
            "caption": caption,
            "like_count": 0,
            "comment_count": 0,
            "media_type": "image",
            "thumbnail_url": "https://picsum.photos/id/200/800/800",
            "taken_at": datetime.utcnow().isoformat()
        }
        self.mock_posts.insert(0, new_post)
        self.mock_comments[new_post_id] = []
        return new_post_id
        
    def post_reel(self, video_path: str, caption: str) -> str:
        print(f"[Simulated Client] Uploading reel '{video_path}' with caption: '{caption}'")
        self.posts_count += 1
        new_post_id = f"mock_post_{random.randint(200, 999)}"
        new_post = {
            "id": new_post_id,
            "caption": caption,
            "like_count": 0,
            "comment_count": 0,
            "media_type": "video",
            "thumbnail_url": "https://picsum.photos/id/300/800/800",
            "taken_at": datetime.utcnow().isoformat()
        }
        self.mock_posts.insert(0, new_post)
        self.mock_comments[new_post_id] = []
        return new_post_id
        
    def get_direct_messages(self) -> list:
        return self.mock_dms
        
    def reply_to_direct_message(self, thread_id: str, text: str) -> bool:
        print(f"[Simulated Client] Replying to DM thread '{thread_id}': '{text}'")
        for dm in self.mock_dms:
            if dm["id"] == thread_id:
                dm["is_unread"] = False
                dm["text"] = f"Reply: {text}"  # Simulating update
                return True
        return False
        
    def get_comments(self, media_id: str) -> list:
        return self.mock_comments.get(media_id, [])
        
    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        print(f"[Simulated Client] Replying to comment '{comment_id}': '{text}'")
        for media_id, comments in self.mock_comments.items():
            for comm in comments:
                if comm["id"] == comment_id:
                    comm["is_unread"] = False
                    return True
        return False
        
    def get_recent_posts(self, limit: int = 5) -> list:
        return self.mock_posts[:limit]


class LiveInstagramClient(InstagramClientInterface):
    """Actual Instagram client wrapping instagrapi.Client."""
    
    def __init__(self, username, password, totp_seed="", session_path=None):
        self.username = username
        self.password = password
        self.totp_seed = totp_seed
        self.session_path = session_path or _session_path_for(username)
        
        from instagrapi import Client
        self.cl = Client()
        self.logged_in = False

    def _verification_code(self) -> str:
        value = (self.totp_seed or "").strip().replace(" ", "")
        if not value:
            return ""
        if value.isdigit() and len(value) == 6:
            return value
        try:
            import pyotp
        except ImportError as exc:
            raise RuntimeError("Install pyotp or provide the current 6-digit Instagram 2FA code.") from exc
        return pyotp.TOTP(value).now()

    def _challenge_code_handler(self, username: str, choice) -> str:
        return self._verification_code()

    def _login_client(self) -> None:
        self.cl.challenge_code_handler = self._challenge_code_handler
        self.cl.login(self.username, self.password, verification_code=self._verification_code())
        
    def login(self) -> bool:
        try:
            # Check for existing login session settings to avoid frequent logins which trigger blocks
            if os.path.exists(self.session_path):
                try:
                    self.cl.load_settings(self.session_path)
                    self._login_client()
                    # Verify session with simple request
                    self.cl.get_timeline_feed()
                    self.logged_in = True
                    print("[Instagram Client] Logged in successfully using saved session.")
                    return True
                except Exception as e:
                    print(f"[Instagram Client] Saved session invalid, performing clean login. Error: {e}")
                    # Remove broken session file
                    if os.path.exists(self.session_path):
                        os.remove(self.session_path)
            
            # Clean login
            self._login_client()
            
            self.cl.dump_settings(self.session_path)
            self.logged_in = True
            print("[Instagram Client] Logged in successfully.")
            return True
        except Exception as e:
            print(f"[Instagram Client] Login failed: {e}")
            self.logged_in = False
            raise e
            
    def get_profile_info(self) -> dict:
        if not self.logged_in:
            self.login()
        user_info = self.cl.user_info(self.cl.user_id)
        return {
            "username": user_info.username,
            "followers": user_info.follower_count,
            "following": user_info.following_count,
            "posts_count": user_info.media_count,
            "full_name": user_info.full_name,
            "biography": user_info.biography
        }
        
    def post_photo(self, image_path: str, caption: str) -> str:
        if not self.logged_in:
            self.login()
        # instagrapi handles resizing and uploading
        media = self.cl.photo_upload(image_path, caption)
        return media.pk
        
    def post_reel(self, video_path: str, caption: str) -> str:
        if not self.logged_in:
            self.login()
        media = self.cl.clip_upload(video_path, caption)
        return media.pk
        
    def get_direct_messages(self) -> list:
        if not self.logged_in:
            self.login()
        threads = self.cl.direct_threads(limit=10)
        unread_dms = []
        for thread in threads:
            # thread.unread_item_count has unread counts
            if thread.unread_item_count > 0 and thread.messages:
                last_message = thread.messages[0]
                unread_dms.append({
                    "id": thread.id,
                    "username": last_message.user_id, # Instagrapi can map user IDs
                    "text": last_message.text,
                    "timestamp": last_message.timestamp.isoformat() if hasattr(last_message, 'timestamp') else datetime.utcnow().isoformat(),
                    "is_unread": True
                })
        return unread_dms
        
    def reply_to_direct_message(self, thread_id: str, text: str) -> bool:
        if not self.logged_in:
            self.login()
        self.cl.direct_send(text, thread_ids=[thread_id])
        return True
        
    def get_comments(self, media_id: str) -> list:
        if not self.logged_in:
            self.login()
        comments = self.cl.media_comments(media_id, amount=10)
        formatted_comments = []
        for c in comments:
            formatted_comments.append({
                "id": c.pk,
                "username": c.user.username,
                "text": c.text,
                "is_unread": True # Live comments will need custom tracking
            })
        return formatted_comments
        
    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        if not self.logged_in:
            self.login()
        # Note: Replying to comment requires the media ID and comment ID.
        # Instagrapi supports direct reply via comment_create
        # We find the media ID based on the comment's context if necessary, or pass directly
        self.cl.comment_create(text, comment_id)
        return True
        
    def get_recent_posts(self, limit: int = 5) -> list:
        if not self.logged_in:
            self.login()
        medias = self.cl.user_medias(self.cl.user_id, amount=limit)
        posts = []
        for m in medias:
            posts.append({
                "id": m.pk,
                "caption": m.caption_text,
                "like_count": m.like_count,
                "comment_count": m.comment_count,
                "media_type": "video" if m.media_type == 2 else "image",
                "thumbnail_url": m.thumbnail_url if hasattr(m, 'thumbnail_url') and m.thumbnail_url else "https://picsum.photos/id/20/800/800",
                "taken_at": m.taken_at.isoformat() if m.taken_at else datetime.utcnow().isoformat()
            })
        return posts


def get_instagram_client() -> InstagramClientInterface:
    """Factory function returning active mock or live client based on settings."""
    if config.SIMULATION_MODE or not config.INSTAGRAM_USERNAME or not config.INSTAGRAM_PASSWORD:
        print("[Instagram API] Initializing Simulation/Mock Client...")
        return MockInstagramClient(username=config.INSTAGRAM_USERNAME or "simulated_agent")
    else:
        try:
            print("[Instagram API] Initializing Live Connection...")
            client = LiveInstagramClient(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD, config.INSTAGRAM_2FA_SEED)
            client.login()
            return client
        except Exception as e:
            print(f"[Instagram API] Fallback to Mock Client due to live login failure: {e}")
            return MockInstagramClient(username=config.INSTAGRAM_USERNAME)


def _session_path_for(username: str) -> str:
    clean = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in (username or "account").lower().lstrip("@"))
    digest = hashlib.sha256(f"live:{clean}".encode("utf-8")).hexdigest()[:10]
    session_dir = Path("media") / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    return str(session_dir / f"live_{clean[:42]}_{digest}.json")
