# Data Wrangler's Toolkit
# A multi-featured desktop application for cleaning and visualizing data.
# Dependencies: ttkbootstrap, pandas, numpy, matplotlib, openpyxl

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import os

class App(ttk.Window):
    def __init__(self):
        # Initialize with the "superhero" dark theme
        super().__init__(themename="superhero")

        self.df = None
        self.history = []

        self.title("Data Wrangler's Toolkit")
        self.geometry("1200x800")

        # --- Main container frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=BOTH, expand=True)

        # --- Top frame for file operations ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=X, pady=5)

        self.load_button = ttk.Button(top_frame, text="Load CSV/Excel", command=self.load_file, bootstyle="primary")
        self.load_button.pack(side=LEFT, padx=(0, 10))
        self.export_button = ttk.Button(top_frame, text="Export to CSV", command=self.export_to_csv, bootstyle="success")
        self.export_button.pack(side=LEFT)
        self.file_label = ttk.Label(top_frame, text="No file loaded.")
        self.file_label.pack(side=LEFT, padx=10)
        
        # --- Middle frame for actions ---
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        action_frame.pack(fill=X, pady=10)
        
        self.remove_duplicates_button = ttk.Button(action_frame, text="Remove Duplicates", command=self.remove_duplicates, bootstyle="danger-outline")
        self.remove_duplicates_button.pack(side=LEFT, padx=(0, 10))

        ttk.Label(action_frame, text="Handle Missing Values in:").pack(side=LEFT, padx=(10, 5))
        self.column_selector = ttk.Combobox(action_frame, state="readonly", width=15)
        self.column_selector.pack(side=LEFT, padx=(0, 5))
        self.action_selector = ttk.Combobox(action_frame, state="readonly", width=18,
                                            values=["Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with Value:"])
        self.action_selector.pack(side=LEFT, padx=(0, 5))
        self.action_selector.bind("<<ComboboxSelected>>", self.toggle_custom_entry)
        self.custom_value_entry = ttk.Entry(action_frame, width=10, state="disabled")
        self.custom_value_entry.pack(side=LEFT, padx=(0, 5))
        self.apply_action_button = ttk.Button(action_frame, text="Apply", command=self.handle_missing_values, bootstyle="info")
        self.apply_action_button.pack(side=LEFT)
        
        ttk.Separator(action_frame, orient='vertical').pack(side=LEFT, padx=15, fill='y')
        ttk.Label(action_frame, text="Generate Plot:").pack(side=LEFT)
        self.plot_type_selector = ttk.Combobox(action_frame, state="readonly", width=20,
                                               values=["Histogram (Numeric)", "Bar Chart (Categorical)"])
        self.plot_type_selector.pack(side=LEFT, padx=5)
        self.plot_button = ttk.Button(action_frame, text="Generate Plot", command=self.generate_plot, bootstyle="info")
        self.plot_button.pack(side=LEFT)

        # --- PanedWindow for resizable bottom section ---
        bottom_pane = ttk.PanedWindow(main_frame, orient=HORIZONTAL)
        bottom_pane.pack(fill=BOTH, expand=True, pady=10)

        # Left Pane: Treeview for data display
        tree_frame = ttk.Frame(bottom_pane, padding=5)
        self.tree = ttk.Treeview(tree_frame, show='headings', bootstyle="primary")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview, bootstyle="round")
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview, bootstyle="round")
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=hsb.set)
        bottom_pane.add(tree_frame, weight=3)

        # Right Pane: History Log
        history_frame = ttk.LabelFrame(bottom_pane, text="Action History", padding=5)
        self.history_text = ttk.Text(history_frame, height=10, width=40, state="disabled", wrap="word")
        self.history_text.pack(side=LEFT, fill=BOTH, expand=True)
        history_sb = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_text.yview, bootstyle="round")
        history_sb.pack(side='right', fill='y')
        self.history_text.config(yscrollcommand=history_sb.set)
        bottom_pane.add(history_frame, weight=1)

    def log_action(self, message):
        """Adds a timestamped message to the history log."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.history.append(log_message)
        
        self.history_text.config(state="normal")
        self.history_text.insert(END, log_message + "\n")
        self.history_text.see(END)
        self.history_text.config(state="disabled")

    def clear_history(self):
        """Clears the history log UI and the internal list."""
        self.history.clear()
        self.history_text.config(state="normal")
        self.history_text.delete('1.0', END)
        self.history_text.config(state="disabled")

    def load_file(self):
        """Loads a CSV or Excel file into a pandas DataFrame."""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")]
        )
        if not filepath: return
        
        try:
            self.df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
            self.update_treeview(self.df)
            self.file_label.config(text=os.path.basename(filepath))
            self.clear_history()
            self.log_action(f"Loaded {self.df.shape[0]} rows from {os.path.basename(filepath)}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def update_treeview(self, df):
        """Clears and repopulates the treeview with a dataframe."""
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
        self.column_selector.set('') # Clear selection

    def remove_duplicates(self):
        """Removes duplicate rows from the DataFrame."""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return

        original_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        rows_removed = original_rows - len(self.df)
        
        if rows_removed > 0:
            messagebox.showinfo("Success", f"Removed {rows_removed} duplicate row(s).")
            self.log_action(f"Removed {rows_removed} duplicate row(s).")
            self.update_treeview(self.df)
        else:
            messagebox.showinfo("Info", "No duplicate rows found.")
            self.log_action("Attempted to remove duplicates: None found.")

    def toggle_custom_entry(self, event=None):
        """Enables or disables the custom value entry box."""
        if self.action_selector.get() == "Fill with Value:":
            self.custom_value_entry.config(state="normal")
        else:
            self.custom_value_entry.config(state="disabled")

    def handle_missing_values(self):
        """Applies a selected action to handle missing values in a column."""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return

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
            self.log_action(f"Applied '{action}' to column '{column}'.")
            self.update_treeview(self.df)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def export_to_csv(self):
        """Exports the current DataFrame to a new CSV file."""
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export.")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not filepath: return

            self.df.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Data successfully exported to:\n{filepath}")
            self.log_action(f"Exported data to {os.path.basename(filepath)}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {e}")
            
    def generate_plot(self):
        """Generates a plot from a selected column in a new window."""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return

        column = self.column_selector.get()
        plot_type = self.plot_type_selector.get()

        if not column or not plot_type:
            messagebox.showwarning("Warning", "Please select a column and a plot type.")
            return
            
        plot_window = ttk.Toplevel(self)
        plot_window.title(f"Plot for {column}")
        plot_window.geometry("800x600")

        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)

        try:
            if plot_type == "Histogram (Numeric)":
                if not pd.api.types.is_numeric_dtype(self.df[column]):
                    messagebox.showerror("Error", "Histogram requires a numeric column.")
                    plot_window.destroy()
                    return
                self.df[column].dropna().plot(kind='hist', ax=ax, bins=30, title=f'Histogram of {column}')
                ax.set_xlabel(column)
                ax.set_ylabel("Frequency")
            elif plot_type == "Bar Chart (Categorical)":
                value_counts = self.df[column].value_counts().nlargest(20)
                value_counts.plot(kind='bar', ax=ax, title=f'Bar Chart of {column}')
                ax.set_xlabel(column)
                ax.set_ylabel("Count")
                fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate plot: {e}")
            plot_window.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()