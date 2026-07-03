# desktop_app.py
"""
Desktop GUI version of the Instagram AI Agent.
Features (core subset of the original Streamlit app):
- Strategy selection / creation
- Media upload & caption generation
- Schedule a post
- Manual trigger for auto‑engagement tasks
- Simple analytics summary

The implementation re‑uses the existing backend modules:
* `database.py` (SQLAlchemy models & session helpers)
* `instagram_client.py` (real or mock Instagram client)
* `agent.py` (caption / reply generation)
* `instagram_client.create_gradient_post_image` (gradient placeholder images)

Tkinter is part of the Python standard library, so no extra GUI dependency is required.
"""

import os
import sys
import random
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

# Backend imports (project modules are in the same directory)
sys.path.append(str(Path(__file__).parent))
from database import (
    init_db,
    Strategy,
    Post,
    EngagementLog,
    AnalyticsSnapshot,
    with_db,
)
from instagram_client import get_instagram_client
from agent import (
    generate_caption_and_hashtags,
    generate_comment_reply,
    generate_dm_reply,
)

# ----------------------------------------------------------------------
# Helper: Gradient image generator (replicates the function from app.py)
# ----------------------------------------------------------------------
def create_gradient_post_image(topic: str, text_caption: str, filepath: str) -> str:
    """Generate a simple gradient placeholder image.
    The function mirrors the one in the original Streamlit version.
    """
    img = Image.new("RGB", (1080, 1080), "#0f111a")
    draw = ImageDraw.Draw(img)
    for _ in range(3):
        x = random.randint(100, 980)
        y = random.randint(100, 980)
        r = random.randint(200, 450)
        color = random.choice(["#7c3aed", "#06b6d4", "#ec4899", "#8b5cf6"])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    overlay = Image.new("RGBA", (1080, 1080), (15, 17, 26, 210))
    img.paste(overlay, (0, 0), overlay)
    draw.rounded_rectangle([(40, 40), (1040, 1040)], radius=24, outline="rgba(255, 255, 255, 0.1)", width=3)
    draw.text((80, 100), "AUTO POST BY AURA AI", fill="#9ca3af")
    clean_topic = topic if topic else "Coding Insights"
    draw.text((80, 200), f"Topic: {clean_topic.upper()}", fill="#06b6d4")
    # Very simple word‑wrap for the caption text
    words = text_caption.split()
    lines = []
    cur = []
    for w in words:
        if len(" ".join(cur + [w])) < 35:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    y_offset = 350
    for line in lines[:10]:
        draw.text((80, y_offset), line, fill="#ffffff")
        y_offset += 55
    img.save(filepath)
    return filepath

# ----------------------------------------------------------------------
# Main Application Class
# ----------------------------------------------------------------------
class InstagramAIAgentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ Instagram AI Agent – Desktop App")
        self.geometry("1200x800")
        self.configure(bg="#080a0f")
        # Initialise DB and client
        init_db()
        self.db = None
        self.ig = get_instagram_client()
        # UI
        self._create_widgets()
        self._load_strategies()
        self._refresh_analytics()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#080a0f")
        style.configure("TFrame", background="#080a0f")
        style.configure("TLabel", background="#080a0f", foreground="#e0e0ff")
        style.configure("TButton", background="#4f46e5", foreground="#ffffff")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_strategy = ttk.Frame(notebook)
        self.tab_creator = ttk.Frame(notebook)
        self.tab_automation = ttk.Frame(notebook)
        self.tab_analytics = ttk.Frame(notebook)
        notebook.add(self.tab_strategy, text="Strategy")
        notebook.add(self.tab_creator, text="Post Creator")
        notebook.add(self.tab_automation, text="Automation")
        notebook.add(self.tab_analytics, text="Analytics")

        self._build_strategy_tab()
        self._build_creator_tab()
        self._build_automation_tab()
        self._build_analytics_tab()

    # ------------------------------------------------------------------
    # Strategy Tab
    # ------------------------------------------------------------------
    def _build_strategy_tab(self):
        f = self.tab_strategy
        ttk.Label(f, text="Select or create a strategy", font=("Helvetica", 14)).pack(pady=10)
        self.strategy_var = tk.StringVar()
        self.strategy_combo = ttk.Combobox(f, textvariable=self.strategy_var, state="readonly", width=40)
        self.strategy_combo.pack(pady=5)
        ttk.Button(f, text="Load", command=self._load_selected_strategy).pack(pady=5)
        ttk.Separator(f, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(f, text="New Strategy", font=("Helvetica", 12, "underline")).pack(pady=5)
        ttk.Label(f, text="Name:").pack(anchor="w", padx=20)
        self.new_name = ttk.Entry(f, width=30)
        self.new_name.pack(pady=2)
        ttk.Label(f, text="Brand Voice:").pack(anchor="w", padx=20)
        self.new_voice = ttk.Entry(f, width=30)
        self.new_voice.pack(pady=2)
        ttk.Label(f, text="Niche:").pack(anchor="w", padx=20)
        self.new_niche = ttk.Entry(f, width=30)
        self.new_niche.pack(pady=2)
        ttk.Button(f, text="Save Strategy", command=self._save_new_strategy).pack(pady=10)

    @with_db
    def _load_strategies(self, db):
        strategies = db.query(Strategy).order_by(Strategy.created_at.desc()).all()
        self.strategy_map = {s.name: s.id for s in strategies}
        self.strategy_combo["values"] = list(self.strategy_map.keys())
        if strategies:
            self.strategy_combo.current(0)
            self.current_strategy = strategies[0]
        else:
            self.current_strategy = None

    def _load_selected_strategy(self):
        name = self.strategy_var.get()
        if not name:
            messagebox.showwarning("Select", "Choose a strategy first.")
            return
        sid = self.strategy_map.get(name)
        @with_db
        def fetch(db):
            self.current_strategy = db.query(Strategy).filter(Strategy.id == sid).first()
        fetch()
        messagebox.showinfo("Loaded", f"Strategy '{name}' loaded.")

    def _save_new_strategy(self):
        name = self.new_name.get().strip()
        voice = self.new_voice.get().strip()
        niche = self.new_niche.get().strip()
        if not (name and voice and niche):
            messagebox.showerror("Missing", "All fields required.")
            return
        @with_db
        def insert(db):
            if db.query(Strategy).filter(Strategy.name == name).first():
                messagebox.showerror("Duplicate", "Strategy name already exists.")
                return
            db.add(Strategy(name=name, brand_voice=voice, niche=niche))
            db.commit()
        insert()
        messagebox.showinfo("Saved", f"Strategy '{name}' saved.")
        self._load_strategies()

    # ------------------------------------------------------------------
    # Post Creator Tab
    # ------------------------------------------------------------------
    def _build_creator_tab(self):
        f = self.tab_creator
        ttk.Label(f, text="Create a new Instagram post", font=("Helvetica", 14)).pack(pady=10)
        # Media picker
        media_f = ttk.Frame(f)
        media_f.pack(fill="x", pady=5, padx=10)
        ttk.Label(media_f, text="Media file:").grid(row=0, column=0, sticky="w")
        self.media_path_var = tk.StringVar()
        ttk.Entry(media_f, textvariable=self.media_path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(media_f, text="Browse", command=self._browse_media).grid(row=0, column=2)
        # Caption area
        ttk.Label(f, text="Generated caption (editable):").pack(anchor="w", padx=10)
        self.caption_box = tk.Text(f, height=5, width=80)
        self.caption_box.pack(padx=10, pady=5)
        # Schedule
        schedule_f = ttk.Frame(f)
        schedule_f.pack(fill="x", pady=5, padx=10)
        ttk.Label(schedule_f, text="Schedule (YYYY-MM-DD HH:MM):").grid(row=0, column=0, sticky="w")
        self.schedule_entry = ttk.Entry(schedule_f, width=25)
        self.schedule_entry.grid(row=0, column=1, padx=5)
        self.schedule_entry.insert(0, (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"))
        ttk.Button(f, text="Generate Caption & Queue", command=self._generate_and_queue).pack(pady=12)

    def _browse_media(self):
        path = filedialog.askopenfilename(
            title="Select image or video",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.mp4"), ("All files", "*")],
        )
        if path:
            self.media_path_var.set(path)

    def _generate_and_queue(self):
        if not self.current_strategy:
            messagebox.showerror("Strategy", "Load or create a strategy first.")
            return
        media_path = self.media_path_var.get().strip()
        if not media_path:
            messagebox.showerror("Media", "Select a media file.")
            return
        topic = Path(media_path).stem.replace("_", " ")
        gen = generate_caption_and_hashtags(self.current_strategy, topic)
        full_caption = f"{gen['caption']}\n{gen['hashtags']}"
        self.caption_box.delete("1.0", tk.END)
        self.caption_box.insert(tk.END, full_caption)
        # Parse schedule
        try:
            schedule_dt = datetime.strptime(self.schedule_entry.get().strip(), "%Y-%m-%d %H:%M")
        except Exception:
            messagebox.showerror("Schedule", "Enter datetime as YYYY-MM-DD HH:MM")
            return
        @with_db
        def save_post(db):
            post = Post(
                caption=full_caption,
                hashtags=gen['hashtags'],
                media_path=media_path,
                scheduled_at=schedule_dt,
                posted=False,
                strategy_id=self.current_strategy.id,
            )
            db.add(post)
            db.commit()
            messagebox.showinfo("Queued", f"Post scheduled for {schedule_dt}.")
        save_post()

    # ------------------------------------------------------------------
    # Automation Tab
    # ------------------------------------------------------------------
    def _build_automation_tab(self):
        f = self.tab_automation
        ttk.Label(f, text="Run autonomous processes manually", font=("Helvetica", 14)).pack(pady=10)
        ttk.Button(f, text="Process Due Posts", command=self._process_due_posts).pack(pady=5)
        ttk.Button(f, text="Process DMs & Comments", command=self._process_engagement).pack(pady=5)

    def _process_due_posts(self):
        @with_db
        def work(db):
            now = datetime.utcnow()
            due = db.query(Post).filter(Post.posted.is_(False), Post.scheduled_at <= now).all()
            for p in due:
                try:
                    if p.media_path.startswith("media/auto_gen_"):
                        create_gradient_post_image(p.caption.split("\n")[0], p.caption, p.media_path)
                    if "reel" in p.media_path.lower():
                        mid = self.ig.post_reel(p.media_path, p.caption)
                    else:
                        mid = self.ig.post_photo(p.media_path, p.caption)
                    p.posted = True
                    p.instagram_media_id = mid
                    p.posted_at = now
                except Exception as ex:
                    p.error_message = str(ex)
            db.commit()
        work()
        messagebox.showinfo("Done", "Due posts processed.")

    def _process_engagement(self):
        @with_db
        def work(db):
            # DMs
            try:
                dms = self.ig.get_direct_messages()
                for dm in dms:
                    if dm.get("is_unread") and not db.query(EngagementLog).filter(EngagementLog.message_id == dm["id"], EngagementLog.type == "dm").first():
                        reply = generate_dm_reply(self.current_strategy, dm["text"], dm["username"])
                        self.ig.reply_to_direct_message(dm["id"], reply)
                        db.add(EngagementLog(type="dm", username=dm["username"], message_id=dm["id"], input_text=dm["text"], response_text=reply, status="sent"))
            except Exception as e:
                print("DM error", e)
            # Comments on recent posts
            try:
                recent = self.ig.get_recent_posts(limit=2)
                for rp in recent:
                    comments = self.ig.get_comments(rp["id"])
                    for cm in comments:
                        if not db.query(EngagementLog).filter(EngagementLog.message_id == cm["id"], EngagementLog.type == "comment").first():
                            reply = generate_comment_reply(self.current_strategy, cm["text"], cm["username"])
                            self.ig.reply_to_comment(cm["id"], reply)
                            db.add(EngagementLog(type="comment", username=cm["username"], message_id=cm["id"], input_text=cm["text"], response_text=reply, status="sent"))
            except Exception as e:
                print("Comment error", e)
            db.commit()
        work()
        messagebox.showinfo("Done", "Engagement processing finished.")

    # ------------------------------------------------------------------
    # Analytics Tab
    # ------------------------------------------------------------------
    def _build_analytics_tab(self):
        f = self.tab_analytics
        ttk.Label(f, text="Latest analytics snapshot", font=("Helvetica", 14)).pack(pady=10)
        self.analytics_label = ttk.Label(f, text="Loading...", font=("Helvetica", 12), background="#080a0f", foreground="#e0e0ff")
        self.analytics_label.pack(pady=5)
        ttk.Button(f, text="Refresh", command=self._refresh_analytics).pack(pady=5)

    @with_db
    def _refresh_analytics(self, db):
        snap = db.query(AnalyticsSnapshot).order_by(AnalyticsSnapshot.captured_at.desc()).first()
        if snap:
            txt = f"Followers: {snap.total_followers}\nLikes: {snap.total_likes}\nComments: {snap.total_comments}\nCaptured: {snap.captured_at}"
        else:
            txt = "No analytics data yet."
        self.analytics_label.config(text=txt)

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = InstagramAIAgentApp()
    app.mainloop()
