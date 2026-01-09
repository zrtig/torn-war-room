import requests
import customtkinter as ctk
import json
import os
import csv
from tkinter import messagebox, filedialog

CONFIG_FILE = "torn_config.json"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PayoutApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TORN - War-Room Console")
        self.geometry("650x900") # Wider base for better table readability

        # --- DATA STORAGE ---
        self.current_data = []

        # --- UI LAYOUT ---
        # 1. API & Inputs Frame (Fixed height at top)
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=20, fill="x")

        self.api_entry = ctk.CTkEntry(self.top_frame, placeholder_text="API Key", show="*", width=350)
        self.api_entry.grid(row=0, column=0, padx=10, pady=10)
        
        self.remember_var = ctk.BooleanVar(value=True)
        self.remember_cb = ctk.CTkCheckBox(self.top_frame, text="Save Key", variable=self.remember_var)
        self.remember_cb.grid(row=0, column=1)

        self.fetch_btn = ctk.CTkButton(self.top_frame, text="AUTO-FILL WAR", command=self.smart_fetch, fg_color="#1f538d")
        self.fetch_btn.grid(row=0, column=2, padx=10)

        # 2. Main Input Grid
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=5, padx=20, fill="x")

        self.war_id = ctk.CTkEntry(self.input_frame, placeholder_text="War ID")
        self.war_id.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.faction_id = ctk.CTkEntry(self.input_frame, placeholder_text="Faction ID")
        self.faction_id.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.reward = ctk.CTkEntry(self.input_frame, placeholder_text="Cash Reward ($)")
        self.reward.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        self.input_frame.columnconfigure((0,1,2), weight=1)

        # 3. Sliders Frame
        self.slider_frame = ctk.CTkFrame(self)
        self.slider_frame.pack(pady=5, padx=20, fill="x")

        self.hit_label = ctk.CTkLabel(self.slider_frame, text="Weight: 50% Hits / 50% Resp", font=("Roboto", 12))
        self.hit_label.grid(row=0, column=0, padx=20)
        self.hit_slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, command=self.update_hit_label)
        self.hit_slider.set(50)
        self.hit_slider.grid(row=1, column=0, padx=20, pady=(0,10), sticky="ew")

        self.cut_label = ctk.CTkLabel(self.slider_frame, text="Faction Cut: 20%", font=("Roboto", 12))
        self.cut_label.grid(row=0, column=1, padx=20)
        self.cut_slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, command=self.update_cut_label)
        self.cut_slider.set(20)
        self.cut_slider.grid(row=1, column=1, padx=20, pady=(0,10), sticky="ew")
        self.slider_frame.columnconfigure((0,1), weight=1)

        # 4. Action Buttons (Side by Side)
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10, padx=20, fill="x")
        
        self.calc_btn = ctk.CTkButton(self.action_frame, text="CALCULATE PAYOUTS", command=self.calculate, fg_color="#2b7333", height=40)
        self.calc_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.export_btn = ctk.CTkButton(self.action_frame, text="EXPORT CSV", command=self.export_to_csv, fg_color="#a66e00", height=40)
        self.export_btn.grid(row=0, column=1, padx=5, sticky="ew")
        self.action_frame.columnconfigure((0,1), weight=1)

        # 5. THE MAIN TEXT AREA (Expanding to fill all remaining space)
        self.result_box = ctk.CTkTextbox(self, font=("Courier New", 13))
        self.result_box.pack(pady=10, padx=20, fill="both", expand=True)

        # Footer
        self.footer = ctk.CTkLabel(self, text="Developed by car [3581510]", font=("Roboto", 10), text_color="gray")
        self.footer.pack(side="bottom", pady=5)

        self.load_saved_key()

    def update_hit_label(self, val):
        self.hit_label.configure(text=f"Weight: {int(val)}% Hits / {100-int(val)}% Resp")

    def update_cut_label(self, val):
        self.cut_label.configure(text=f"Faction Cut: {int(val)}%")

    def smart_fetch(self):
        key = self.api_entry.get().strip()
        if not key: return
        try:
            u_res = requests.get(f"https://api.torn.com/user/?selections=profile&key={key}").json()
            f_id = u_res.get('faction', {}).get('faction_id')
            self.faction_id.delete(0, "end"); self.faction_id.insert(0, str(f_id))
            w_res = requests.get(f"https://api.torn.com/faction/{f_id}?selections=rankedwars&key={key}").json()
            wars = w_res.get('rankedwars', {})
            latest_id = max(wars.keys(), key=lambda k: wars[k].get('war', {}).get('start', 0))
            self.war_id.delete(0, "end"); self.war_id.insert(0, str(latest_id))
        except Exception as e: messagebox.showerror("Error", "Auto-fill failed. Check API Key.")

    def calculate(self):
        self.save_key()
        key, w_id, f_id = self.api_entry.get().strip(), self.war_id.get().strip(), self.faction_id.get().strip()
        try:
            total_pool = float(self.reward.get().replace('$', '').replace(',', ''))
            cut_pct, hit_weight = self.cut_slider.get()/100, self.hit_slider.get()/100
        except: messagebox.showerror("Error", "Check Reward Amount."); return

        res = requests.get(f"https://api.torn.com/torn/{w_id}?selections=rankedwarreport&key={key}").json()
        members = res.get('rankedwarreport', {}).get('factions', {}).get(f_id, {}).get('members', {})
        if not members: messagebox.showerror("Error", "No data found."); return

        self.current_data = []
        total_f_hits = sum(float(m.get('attacks', 0)) for m in members.values())
        total_f_resp = sum(float(m.get('respect', m.get('respect_earned', m.get('score', 0)))) for m in members.values())
        dist_pool = total_pool * (1 - cut_pct)

        for mid, data in members.items():
            m_hits = float(data.get('attacks', 0))
            m_resp = float(data.get('respect', data.get('respect_earned', data.get('score', 0))))
            h_share = (m_hits / total_f_hits) if total_f_hits > 0 else 0
            r_share = (m_resp / total_f_resp) if total_f_resp > 0 else 0
            final_payout = ((h_share * hit_weight) + (r_share * (1 - hit_weight))) * dist_pool
            
            self.current_data.append({'Name': data.get('name', mid), 'Hits': int(m_hits), 'Resp': round(m_resp, 2), 'Payout': round(final_payout)})

        self.current_data.sort(key=lambda x: x['Payout'], reverse=True)
        output = f"{'MEMBER':<22} | {'HITS':<6} | {'RESP':<9} | {'PAYOUT'}\n" + "-"*60 + "\n"
        for m in self.current_data:
            output += f"{m['Name'][:22]:<22} | {m['Hits']:<6} | {m['Resp']:<9.2f} | ${m['Payout']:,.0f}\n"

        self.result_box.delete("0.0", "end"); self.result_box.insert("0.0", output)

    def export_to_csv(self):
        if not self.current_data: return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Name', 'Hits', 'Resp', 'Payout'])
                writer.writeheader(); writer.writerows(self.current_data)

    def load_saved_key(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f: self.api_entry.insert(0, json.load(f).get("api_key", ""))

    def save_key(self):
        if self.remember_var.get():
            with open(CONFIG_FILE, "w") as f: json.dump({"api_key": self.api_entry.get()}, f)

if __name__ == "__main__":
    app = PayoutApp()
    app.mainloop()
