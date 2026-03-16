# English Poetry Scansion Tool for macOS - v6.0 (Definitive)
#
# This definitive version incorporates a weighted scoring system for meter detection,
# correctly prioritizing content words over function words. It also adds a new,
# separate summary section for standard IPA phonetic transcriptions.
#
# This version should fix the scansion accuracy issues and fulfill all feature requests.
# Author: Gemini
# Date: October 1, 2025

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import pickle
import re
import os

class EnglishScansion:
    def __init__(self, dict_path):
        if not os.path.exists(dict_path):
            raise FileNotFoundError(f"The dictionary file '{dict_path}' was not found. Please run the converter (v5) first.")
        
        with open(dict_path, 'rb') as f:
            self.pronunciation_dict = pickle.load(f)

        self.METERS = {'Iambic': '01', 'Trochaic': '10', 'Anapestic': '001', 'Dactylic': '100', 'Amphibrach': '010'}
        self.VOWELS = "aeiouyAEIOUY"
        self.ACCENT_MAP = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú', 'y': 'ý',
                           'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú', 'Y': 'Ý'}
        self.VOWEL_SOUNDS = re.compile(r'[A-Z]{2,3}[0-9]')
        self.FUNCTION_WORDS = {
            'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from',
            'by', 'with', 'in', 'of', 'is', 'am', 'are', 'was', 'were', 'be', 'being',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
            'should', 'can', 'could', 'may', 'might', 'must', 'as', 'if', 'so', 'my', 'your',
            'his', 'her', 'its', 'our', 'their', 'me', 'you', 'him', 'her', 'it', 'us', 'them'
        }

    def get_word_data(self, word):
        """Looks up a word and returns its processed data tuple and original IPA."""
        lookup_word = word.lower().strip(".,;:!?()\"'")
        if not lookup_word or lookup_word not in self.pronunciation_dict:
            return None, f"<{lookup_word}>", 0, None

        arpabet_list, ipa_raw = self.pronunciation_dict[lookup_word][0]
        stress_pattern, syllable_count = "", 0

        for phoneme in arpabet_list:
            if self.VOWEL_SOUNDS.match(phoneme):
                syllable_count += 1
                stress_pattern += '1' if phoneme.endswith('1') or phoneme.endswith('2') else '0'
        
        return stress_pattern, ' '.join(arpabet_list), syllable_count, ipa_raw

    def analyze_line(self, line):
        words = re.findall(r"[\w']+|[.,!?;:]+", line)
        
        lexical_stress_pattern, word_map = "", []
        
        for word in words:
            if re.match(r"[\w']+", word):
                pattern, _, syllables, _ = self.get_word_data(word)
                if pattern is not None:
                    lexical_stress_pattern += pattern
                    word_map.extend([word.lower()] * syllables)

        line_syllables = len(lexical_stress_pattern)
        if line_syllables == 0:
            return {"original": line, "meter": "Unknown", "score": 1.0, "syllables": 0, "final_stress_pattern": ""}

        # ** NEW WEIGHTED SCORING LOGIC **
        scores = {}
        for name, pattern in self.METERS.items():
            template = (pattern * (line_syllables // len(pattern) + 1))[:line_syllables]
            mismatch_score = 0
            for i in range(line_syllables):
                if lexical_stress_pattern[i] != template[i]:
                    # Penalize mismatches on function words less
                    weight = 0.5 if word_map[i] in self.FUNCTION_WORDS else 1.0
                    mismatch_score += weight
            scores[name] = mismatch_score / line_syllables
        
        best_meter_name = min(scores, key=scores.get)
        best_meter_score = scores[best_meter_name]

        winning_meter_pattern = self.METERS[best_meter_name]
        final_stress_pattern = (winning_meter_pattern * (line_syllables // len(winning_meter_pattern) + 1))[:line_syllables]

        foot_len = len(winning_meter_pattern)
        num_feet = round(line_syllables / foot_len) if foot_len > 0 else 0
        foot_map = {0:"0-foot", 1:"monometer", 2:"dimeter", 3:"trimeter", 4:"tetrameter", 5:"pentameter", 6:"hexameter"}
        meter_desc = f"{best_meter_name} {foot_map.get(num_feet, f'{num_feet}-foot')}"

        return {"original": line, "meter": meter_desc, "score": best_meter_score, "syllables": line_syllables, "final_stress_pattern": final_stress_pattern}

    def format_line(self, line, analysis_result, format_type):
        words = re.findall(r"[\w']+|[^\w']+", line)
        output_parts = []

        if format_type == 'arpabet' or format_type == 'ipa':
            for word in words:
                if re.match(r"[\w']+", word):
                    _, arpabet, _, ipa = self.get_word_data(word)
                    output_parts.append(ipa if format_type == 'ipa' and ipa else f"[{arpabet}]")
                else:
                    output_parts.append(word)
            return " ".join(output_parts)

        final_stress = analysis_result['final_stress_pattern']
        syllable_cursor = 0
        for word in words:
            if not re.match(r"[\w']+", word):
                output_parts.append(word)
                continue

            lexical_pattern, _, num_syllables, _ = self.get_word_data(word)
            if lexical_pattern is None:
                output_parts.append(f"<{word}>")
                continue

            word_stress_segment = final_stress[syllable_cursor : syllable_cursor + num_syllables]
            
            if format_type == 'plus':
                output_parts.append(f"+{word}" if '1' in word_stress_segment else word)
            elif format_type == 'accent':
                temp_word = list(word)
                vowel_groups = list(re.finditer(r'[aeiouy]+', word, re.IGNORECASE))
                for i, stress_char in enumerate(word_stress_segment):
                    if stress_char == '1' and i < len(vowel_groups):
                        vowel_match = vowel_groups[i]
                        pos = vowel_match.start()
                        char_to_stress = temp_word[pos]
                        temp_word[pos] = self.ACCENT_MAP.get(char_to_stress, char_to_stress)
                output_parts.append("".join(temp_word))

            syllable_cursor += num_syllables
        
        return " ".join(output_parts).replace(" ,", ",").replace(" .", ".").strip()

class ScansionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Poetry Scansion Tool")
        self.root.geometry("1000x900")
        self.VOWELS = "aeiouyAEIOUY"

        self.style = ttk.Style()
        try: self.style.theme_use('aqua')
        except tk.TclError: self.style.theme_use('default')
        self.style.configure('TFrame', background='#ECECEC')
        self.style.configure('TButton', font=('Helvetica Neue', 13, 'bold'), padding=10)
        self.style.configure('TLabel', font=('Helvetica Neue', 14), background='#ECECEC')
        self.style.configure('Header.TLabel', font=('Helvetica Neue', 18, 'bold'))
        
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_frame, text="Poetry Scansion Analyzer", style='Header.TLabel').pack(pady=(0, 20))
        self.input_text = scrolledtext.ScrolledText(self.main_frame, height=8, font=("Menlo", 12), wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.input_text.insert(tk.END, "But I will ignite\nIn your eyes a fire\nNow I give you strength\nNow I give you power")

        ttk.Button(self.main_frame, text="Analyze Poem", command=self.perform_scan).pack(pady=15)

        self.output_text = tk.Text(self.main_frame, font=("Menlo", 12), wrap=tk.WORD, background="black", relief=tk.SOLID, borderwidth=1, padx=10, pady=10)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.output_text.tag_configure('vowel', foreground="#9370DB")
        self.output_text.tag_configure('stressed_vowel', foreground="#FF474C", font=("Menlo", 12, "bold"))
        self.output_text.tag_configure('consonant', foreground="#FFC700")
        self.output_text.tag_configure('punctuation', foreground="#32CD32")
        self.output_text.tag_configure('info', foreground="white")
        self.output_text.tag_configure('separator', foreground="#555555")
        self.output_text.tag_configure('header', foreground="white", font=("Menlo", 14, "bold", "underline"), justify='center')

        self.output_text.config(state=tk.DISABLED)

        try:
            self.scanner = EnglishScansion(dict_path="english_phonetic_dict.pkl")
        except Exception as e:
            messagebox.showerror("Fatal Error", str(e))
            self.root.destroy()

    def perform_scan(self):
        poem_text = self.input_text.get("1.0", tk.END)
        if not poem_text.strip(): return

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        accented_poem_lines, ipa_poem_lines = [], []

        for line in poem_text.strip().split('\n'):
            if not line.strip():
                self.output_text.insert(tk.END, '\n')
                continue

            analysis = self.scanner.analyze_line(line)
            
            accented_line = self.scanner.format_line(line, analysis, 'accent')
            accented_poem_lines.append(accented_line)
            ipa_poem_lines.append(self.scanner.format_line(line, analysis, 'ipa'))

            self.render_color_line(self.scanner.format_line(line, analysis, 'plus') + "\n")
            self.render_color_line(accented_line + "\n")
            self.output_text.insert(tk.END, self.scanner.format_line(line, analysis, 'arpabet') + "\n", 'info')
            
            info_str = f"Meter: {analysis['meter']} | Syllables: {analysis['syllables']} | Mismatch Score: {analysis['score']:.2f}\n"
            self.output_text.insert(tk.END, info_str, 'info')
            self.output_text.insert(tk.END, "-" * 70 + "\n", 'separator')

        # Render Summaries
        self.output_text.insert(tk.END, "\n\n")
        self.output_text.insert(tk.END, "Stressed Poem Summary\n", 'header')
        self.output_text.insert(tk.END, "\n")
        for line in accented_poem_lines:
            self.render_color_line(line + "\n")

        self.output_text.insert(tk.END, "\n\n")
        self.output_text.insert(tk.END, "IPA Phonetic Transcription\n", 'header')
        self.output_text.insert(tk.END, "\n")
        for line in ipa_poem_lines:
            self.output_text.insert(tk.END, line + "\n", 'info')

        self.output_text.config(state=tk.DISABLED)

    def render_color_line(self, text):
        accented_vowels = "áéíóúýÁÉÍÓÚÝ"
        for char in text:
            tag = 'info'
            if char in accented_vowels: tag = 'stressed_vowel'
            elif char in self.VOWELS: tag = 'vowel'
            elif char.isalpha(): tag = 'consonant'
            elif char in "<>": tag = 'separator'
            elif char in ".,;:!?'\"": tag = 'punctuation'
            elif char == '+': tag = 'stressed_vowel'
            self.output_text.insert(tk.END, char, tag)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScansionApp(root)
    root.mainloop()
