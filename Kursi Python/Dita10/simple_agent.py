import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


NVIDIA_API_KEY = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "openai/gpt-oss-20b"

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "Je nje AI Agent i thjeshte dhe i dobishem. "
        "Pergjigju qarte dhe shkurt ne gjuhen e perdoruesit."
    ),
}

BG = "#F1F5F9"
CARD = "#FFFFFF"
CHAT_BG = "#F8FAFC"
TEXT = "#0F172A"
MUTED = "#64748B"
PRIMARY = "#4F46E5"
PRIMARY_HOVER = "#4338CA"
SUCCESS = "#10B981"
BORDER = "#E2E8F0"
ERROR = "#DC2626"


class SimpleAgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple AI Agent")
        self.root.geometry("860x680")
        self.root.minsize(640, 500)
        self.root.configure(bg=BG)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.client = None
        self.messages = [SYSTEM_MESSAGE.copy()]
        self.is_loading = False

        self.configure_styles()
        self.build_header()
        self.build_chat()
        self.build_composer()

        self.add_to_chat("Agent", "Pershendetje! Si mund te te ndihmoj sot?")
        self.message_entry.focus_set()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure(
            "Title.TLabel",
            background=CARD,
            foreground=TEXT,
            font=("Segoe UI Semibold", 17),
        )
        style.configure(
            "Subtitle.TLabel",
            background=CARD,
            foreground=MUTED,
            font=("Segoe UI", 9),
        )

    def build_header(self):
        header = ttk.Frame(self.root, style="Card.TFrame", padding=(24, 16))
        header.grid(row=0, column=0, sticky="ew")

        logo = tk.Label(
            header,
            text="AI",
            bg=PRIMARY,
            fg="white",
            font=("Segoe UI Semibold", 13),
            width=3,
            height=1,
            padx=5,
            pady=7,
        )
        logo.pack(side="left", padx=(0, 12))

        title_box = ttk.Frame(header, style="Card.TFrame")
        title_box.pack(side="left")
        ttk.Label(title_box, text="Simple AI Agent", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            title_box,
            text="Asistenti yt me NVIDIA AI",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        self.new_chat_button = self.make_button(
            header,
            "Bisede e re",
            self.new_chat,
            background="#EEF2FF",
            foreground=PRIMARY,
            hover="#E0E7FF",
        )
        self.new_chat_button.pack(side="right")

    def build_chat(self):
        chat_card = tk.Frame(
            self.root,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        chat_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=24,
            pady=(20, 12),
        )
        chat_card.grid_columnconfigure(0, weight=1)
        chat_card.grid_rowconfigure(0, weight=1)

        self.chat = scrolledtext.ScrolledText(
            chat_card,
            wrap="word",
            height=10,
            state="disabled",
            bg=CHAT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 11),
            padx=22,
            pady=18,
            spacing1=2,
            spacing3=8,
        )
        self.chat.grid(row=0, column=0, sticky="nsew")

        self.chat.tag_configure(
            "agent_name",
            foreground=SUCCESS,
            font=("Segoe UI Semibold", 10),
            spacing1=8,
        )
        self.chat.tag_configure(
            "user_name",
            foreground=PRIMARY,
            font=("Segoe UI Semibold", 10),
            justify="right",
            spacing1=8,
        )
        self.chat.tag_configure(
            "agent_message",
            foreground=TEXT,
            lmargin1=0,
            lmargin2=0,
            rmargin=80,
        )
        self.chat.tag_configure(
            "user_message",
            foreground=TEXT,
            justify="right",
            lmargin1=80,
            lmargin2=80,
        )
        self.chat.tag_configure(
            "error_name",
            foreground=ERROR,
            font=("Segoe UI Semibold", 10),
        )
        self.chat.tag_configure("error_message", foreground=ERROR)
        self.chat.tag_configure(
            "typing_message",
            foreground=MUTED,
            font=("Segoe UI", 10, "italic"),
        )

    def build_composer(self):
        composer = tk.Frame(
            self.root,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        composer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 10))

        tk.Label(
            composer,
            text="Shkruaj mesazhin tend",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w", pady=(0, 8))

        input_row = tk.Frame(composer, bg=CARD)
        input_row.pack(fill="x")

        input_border = tk.Frame(
            input_row,
            bg=CHAT_BG,
            highlightbackground="#CBD5E1",
            highlightcolor=PRIMARY,
            highlightthickness=1,
        )
        input_border.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.message_entry = tk.Text(
            input_border,
            height=3,
            wrap="word",
            bg=CHAT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 11),
            padx=12,
            pady=10,
        )
        self.message_entry.pack(fill="both", expand=True)
        self.message_entry.bind("<Return>", self.handle_enter)

        self.send_button = self.make_button(
            input_row,
            "Dergo",
            self.send_message,
            background=PRIMARY,
            foreground="white",
            hover=PRIMARY_HOVER,
            padx=22,
            pady=11,
        )
        self.send_button.pack(side="right", anchor="s")

        status_bar = ttk.Frame(self.root, style="App.TFrame", padding=(26, 0, 26, 12))
        status_bar.grid(row=3, column=0, sticky="ew")

        self.status_dot = tk.Label(
            status_bar,
            text="o",
            bg=BG,
            fg=SUCCESS,
            font=("Segoe UI", 9),
        )
        self.status_dot.pack(side="left")

        self.status_label = tk.Label(
            status_bar,
            text="Gati",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side="left", padx=(5, 0))

        tk.Label(
            status_bar,
            text="Enter per te derguar  |  Shift + Enter per rresht te ri",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right")

    def make_button(
        self,
        parent,
        text,
        command,
        background,
        foreground,
        hover,
        padx=16,
        pady=8,
    ):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg=foreground,
            activebackground=hover,
            activeforeground=foreground,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=padx,
            pady=pady,
        )
        button.bind("<Enter>", lambda event: button.config(bg=hover))
        button.bind("<Leave>", lambda event: button.config(bg=background))
        return button

    def add_to_chat(self, sender, message):
        tag_prefix = "user" if sender == "Ti" else "agent"
        if sender == "Gabim":
            tag_prefix = "error"

        self.chat.config(state="normal")
        self.chat.insert("end", f"{sender}\n", f"{tag_prefix}_name")
        self.chat.insert("end", f"{message}\n\n", f"{tag_prefix}_message")
        self.chat.config(state="disabled")
        self.chat.see("end")

    def show_typing(self):
        self.chat.config(state="normal")
        self.chat.mark_set("typing_start", "end-1c")
        self.chat.mark_gravity("typing_start", "left")
        self.chat.insert("end", "Agent\n", "agent_name")
        self.chat.insert("end", "Agent po mendon...\n\n", "typing_message")
        self.chat.mark_set("typing_end", "end-1c")
        self.chat.config(state="disabled")
        self.chat.see("end")

    def remove_typing(self):
        if "typing_start" not in self.chat.mark_names():
            return

        self.chat.config(state="normal")
        self.chat.delete("typing_start", "typing_end")
        self.chat.mark_unset("typing_start", "typing_end")
        self.chat.config(state="disabled")

    def new_chat(self):
        self.messages = [SYSTEM_MESSAGE.copy()]
        self.chat.config(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.config(state="disabled")
        self.add_to_chat("Agent", "Filluam nje bisede te re. Cfare ke ne mendje?")
        self.set_status("Gati", SUCCESS)
        self.message_entry.focus_set()

    def handle_enter(self, event):
        if event.state & 0x0001:
            return None
        self.send_message()
        return "break"

    def send_message(self):
        if self.is_loading:
            return

        message = self.message_entry.get("1.0", "end-1c").strip()

        if (
            not NVIDIA_API_KEY.strip()
            or NVIDIA_API_KEY == "VENDOS_NVIDIA_API_KEY_TE_RI_KETU"
        ):
            messagebox.showwarning(
                "API key mungon",
                "Vendos API key te ri te konstanta NVIDIA_API_KEY ne kod.",
            )
            return

        if not message:
            return

        self.message_entry.delete("1.0", "end")
        self.add_to_chat("Ti", message)
        self.show_typing()
        self.set_loading(True)

        threading.Thread(
            target=self.call_openai,
            args=(message,),
            daemon=True,
        ).start()

    def call_openai(self, message):
        try:
            from openai import OpenAI

            if self.client is None:
                self.client = OpenAI(
                    base_url=NVIDIA_BASE_URL,
                    api_key=NVIDIA_API_KEY,
                )

            request_messages = self.messages + [{"role": "user", "content": message}]
            response = self.client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=request_messages,
                temperature=0.7,
                top_p=1,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content or "Nuk mora pergjigje."
            self.messages = request_messages + [
                {"role": "assistant", "content": answer}
            ]
            self.root.after(0, self.show_response, answer)
        except ImportError:
            self.root.after(
                0,
                self.show_error,
                "Paketa openai mungon. Instaloje me: python -m pip install openai",
            )
        except Exception as error:
            self.root.after(0, self.show_error, str(error))

    def show_response(self, message):
        self.remove_typing()
        self.add_to_chat("Agent", message)
        self.set_loading(False)

    def show_error(self, message):
        self.remove_typing()
        self.add_to_chat("Gabim", message)
        self.set_loading(False)

    def set_status(self, text, color):
        self.status_label.config(text=text)
        self.status_dot.config(fg=color)

    def set_loading(self, is_loading):
        self.is_loading = is_loading
        state = "disabled" if is_loading else "normal"
        self.send_button.config(state=state)
        self.new_chat_button.config(state=state)
        self.set_status(
            "Agent po mendon..." if is_loading else "Gati",
            PRIMARY if is_loading else SUCCESS,
        )
        self.message_entry.focus_set()


def main():
    root = tk.Tk()
    SimpleAgentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
