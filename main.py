import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.df = None

        self.title("Data Wrangler's Toolkit")
        self.geometry("800x600")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        self.load_button = ttk.Button(top_frame, text="Load CSV/Excel", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # --- NEW: Export Button ---
        self.export_button = ttk.Button(top_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(side=tk.LEFT)

        self.file_label = ttk.Label(top_frame, text="No file loaded.")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        
        self.remove_duplicates_button = ttk.Button(action_frame, text="Remove Duplicates", command=self.remove_duplicates)
        self.remove_duplicates_button.pack(side=tk.LEFT, padx=(0, 20))

        missing_values_label = ttk.Label(action_frame, text="Handle Missing Values in Column:")
        missing_values_label.pack(side=tk.LEFT, padx=(0, 5))

        self.column_selector = ttk.Combobox(action_frame, state="readonly", width=15)
        self.column_selector.pack(side=tk.LEFT, padx=(0, 5))

        self.action_selector = ttk.Combobox(action_frame, state="readonly", width=18,
                                            values=["Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with Value:"])
        self.action_selector.pack(side=tk.LEFT, padx=(0, 5))
        self.action_selector.bind("<<ComboboxSelected>>", self.toggle_custom_entry)
        
        self.custom_value_entry = ttk.Entry(action_frame, width=10, state="disabled")
        self.custom_value_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.apply_action_button = ttk.Button(action_frame, text="Apply", command=self.handle_missing_values)
        self.apply_action_button.pack(side=tk.LEFT)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tree = ttk.Treeview(bottom_frame, show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=hsb.set)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")]
        )
        if not filepath: return
        
        try:
            self.df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
            self.update_treeview(self.df)
            self.file_label.config(text=filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def update_treeview(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["column"] = list(df.columns)
        self.tree["show"] = "headings"
        for column in self.tree["column"]:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)
        
        df_display = df.replace(np.nan, 'NULL')
        for index, row in df_display.iterrows():
            self.tree.insert("", "end", values=list(row))
            
        self.column_selector['values'] = list(df.columns)

    def remove_duplicates(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return

        original_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        rows_removed = original_rows - len(self.df)
        
        messagebox.showinfo("Success", f"Removed {rows_removed} duplicate row(s).")
        self.update_treeview(self.df)

    def toggle_custom_entry(self, event=None):
        if self.action_selector.get() == "Fill with Value:":
            self.custom_value_entry.config(state="normal")
        else:
            self.custom_value_entry.config(state="disabled")

    def handle_missing_values(self):
        if self.df is None: return
        column = self.column_selector.get()
        action = self.action_selector.get()
        if not column or not action:
            messagebox.showwarning("Warning", "Please select a column and an action.")
            return

        try:
            if action == "Drop Rows":
                self.df.dropna(subset=[column], inplace=True)
            elif action in ["Fill with Mean", "Fill with Median"]:
                if not pd.api.types.is_numeric_dtype(self.df[column]):
                    messagebox.showerror("Error", f"{action} can only be used on numeric columns.")
                    return
                fill_value = self.df[column].mean() if action == "Fill with Mean" else self.df[column].median()
                self.df[column].fillna(fill_value, inplace=True)
            elif action == "Fill with Mode":
                self.df[column].fillna(self.df[column].mode()[0], inplace=True)
            elif action == "Fill with Value:":
                self.df[column].fillna(self.custom_value_entry.get(), inplace=True)
                
            messagebox.showinfo("Success", f"Action '{action}' applied to column '{column}'.")
            self.update_treeview(self.df)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # --- NEW: Export function ---
    def export_to_csv(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export.")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not filepath:
                return

            self.df.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Data successfully exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()