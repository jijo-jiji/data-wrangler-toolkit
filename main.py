import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.df = None  # To store the loaded DataFrame

        self.title("Data Wrangler's Toolkit")
        self.geometry("800x600")

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Top Frame for Controls ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        self.load_button = ttk.Button(top_frame, text="Load CSV/Excel", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))

        self.file_label = ttk.Label(top_frame, text="No file loaded.")
        self.file_label.pack(side=tk.LEFT)
        
        # --- Action Frame for Buttons ---
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        
        self.remove_duplicates_button = ttk.Button(action_frame, text="Remove Duplicates", command=self.remove_duplicates)
        self.remove_duplicates_button.pack(side=tk.LEFT)

        # --- Bottom Frame for Treeview (Data Table) ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # --- Treeview Widget ---
        self.tree = ttk.Treeview(bottom_frame, show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # --- Scrollbars ---
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
        if not filepath:
            return
        
        try:
            if filepath.endswith('.csv'):
                self.df = pd.read_csv(filepath)
            else:
                self.df = pd.read_excel(filepath)
            
            self.update_treeview(self.df)
            self.file_label.config(text=filepath)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def update_treeview(self, df):
        """Helper function to clear and repopulate the treeview with a dataframe."""
        self.tree.delete(*self.tree.get_children())
        self.tree["column"] = list(df.columns)
        self.tree["show"] = "headings"
        for column in self.tree["column"]:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def remove_duplicates(self):
        """Removes duplicate rows from the dataframe and updates the view."""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return

        original_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        new_rows = len(self.df)
        
        rows_removed = original_rows - new_rows
        messagebox.showinfo("Success", f"Removed {rows_removed} duplicate row(s).")
        
        self.update_treeview(self.df)

if __name__ == "__main__":
    app = App()
    app.mainloop()