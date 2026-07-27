import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("450x580")
        self.root.resizable(False, False)

        # Session history (max 5 passwords)
        self.history = []

        self._setup_ui()

    def _setup_ui(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=15)
        header_frame.pack(fill="x")
        ttk.Label(
            header_frame, 
            text="🔐 Password Generator", 
            font=("Helvetica", 16, "bold")
        ).pack()

        # Length Control
        length_frame = ttk.LabelFrame(self.root, text=" Password Length ", padding=10)
        length_frame.pack(fill="x", padx=15, pady=5)

        self.length_var = tk.IntVar(value=16)
        
        slider_frame = ttk.Frame(length_frame)
        slider_frame.pack(fill="x")

        self.length_label = ttk.Label(slider_frame, text="Length: 16", font=("Helvetica", 10, "bold"))
        self.length_label.pack(side="left")

        self.slider = ttk.Scale(
            length_frame, 
            from_=8, 
            to=64, 
            orient="horizontal", 
            variable=self.length_var, 
            command=self._update_length_label
        )
        self.slider.pack(fill="x", pady=5)

        # Character Types Selection
        char_frame = ttk.LabelFrame(self.root, text=" Included Characters ", padding=10)
        char_frame.pack(fill="x", padx=15, pady=5)

        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_numbers = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        ttk.Checkbutton(char_frame, text="Uppercase Letters (A-Z)", variable=self.use_uppercase).pack(anchor="w")
        ttk.Checkbutton(char_frame, text="Lowercase Letters (a-z)", variable=self.use_lowercase).pack(anchor="w")
        ttk.Checkbutton(char_frame, text="Numbers (0-9)", variable=self.use_numbers).pack(anchor="w")
        ttk.Checkbutton(char_frame, text="Symbols (!@#$%...)", variable=self.use_symbols).pack(anchor="w")
        
        ttk.Separator(char_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Checkbutton(char_frame, text="Exclude Ambiguous (0, O, l, 1, I)", variable=self.exclude_ambiguous).pack(anchor="w")

        # Output Section
        output_frame = ttk.LabelFrame(self.root, text=" Generated Password ", padding=10)
        output_frame.pack(fill="x", padx=15, pady=5)

        self.password_entry = ttk.Entry(output_frame, font=("Courier", 12), justify="center")
        self.password_entry.pack(fill="x", pady=5)

        # Strength Bar
        self.strength_label = ttk.Label(output_frame, text="Strength: -", font=("Helvetica", 9, "italic"))
        self.strength_label.pack()

        # Action Buttons
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x", padx=15)

        generate_btn = ttk.Button(btn_frame, text="Generate Password", command=self.generate_password)
        generate_btn.pack(side="left", expand=True, fill="x", padx=2)

        copy_btn = ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side="right", expand=True, fill="x", padx=2)

        # History Display
        history_frame = ttk.LabelFrame(self.root, text=" Session History (Last 5) ", padding=10)
        history_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.history_listbox = tk.Listbox(history_frame, font=("Courier", 9), height=5)
        self.history_listbox.pack(fill="both", expand=True)

        # Initial generation
        self.generate_password()

    def _update_length_label(self, val):
        self.length_label.config(text=f"Length: {int(float(val))}")

    def generate_password(self):
        length = self.length_var.get()
        
        # Build character pools
        pools = []
        ambiguous_chars = set("0Ol1I")

        if self.use_uppercase.get():
            chars = set(string.ascii_uppercase)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append("".join(chars))

        if self.use_lowercase.get():
            chars = set(string.ascii_lowercase)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append("".join(chars))

        if self.use_numbers.get():
            chars = set(string.digits)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append("".join(chars))

        if self.use_symbols.get():
            chars = set("!@#$%^&*()_+-=[]{}|;:,.<>?")
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append("".join(chars))

        # Validation rule: At least 2 character types required
        if len(pools) < 2:
            messagebox.showerror("Selection Error", "Please select at least 2 character types.")
            return

        # Security Rule: Guarantee at least one character from each selected pool
        password_chars = [secrets.choice(pool) for pool in pools]

        # Fill the remaining length from the combined pool
        full_pool = "".join(pools)
        for _ in range(length - len(password_chars)):
            password_chars.append(secrets.choice(full_pool))

        # Cryptographically secure shuffle of the list
        secrets.SystemRandom().shuffle(password_chars)
        password = "".join(password_chars)

        # Display result
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

        # Update strength and history
        self._evaluate_strength(password, len(pools))
        self._update_history(password)

        # Auto-copy to clipboard as per requirements
        try:
            pyperclip.copy(password)
        except Exception:
            pass  # Fallback gracefully if clipboard backend fails

    def _evaluate_strength(self, password, num_types):
        length = len(password)
        
        # Simple entropy-based heuristic
        if length >= 14 and num_types >= 3:
            strength = "Strong 🟢"
        elif length >= 10 and num_types >= 2:
            strength = "Medium 🟡"
        else:
            strength = "Weak 🔴"

        self.strength_label.config(text=f"Strength: {strength}")

    def _update_history(self, password):
        self.history.insert(0, password)
        if len(self.history) > 5:
            self.history.pop()

        self.history_listbox.delete(0, tk.END)
        for pwd in self.history:
            self.history_listbox.insert(tk.END, pwd)

    def copy_to_clipboard(self):
        pwd = self.password_entry.get()
        if pwd:
            pyperclip.copy(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()