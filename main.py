# Data Wrangler's Toolkit - Now with Descriptive Statistics
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
        super().__init__(themename="superhero")

        self.df = None
        self.undo_stack = []
        self.redo_stack = []

        self.title("Data Wrangler's Toolkit")
        self.geometry("1200x850")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=X, pady=5)
        # ... (Top frame widgets are the same)
        self.load_button = ttk.Button(top_frame, text="Load CSV/Excel", command=self.load_file, bootstyle="primary")
        self.load_button.pack(side=LEFT, padx=(0, 10))
        self.export_button = ttk.Button(top_frame, text="Export to CSV", command=self.export_to_csv, bootstyle="success")
        self.export_button.pack(side=LEFT, padx=(0,10))
        self.undo_button = ttk.Button(top_frame, text="Undo", command=self.undo_action, state="disabled")
        self.undo_button.pack(side=LEFT, padx=(0, 5))
        self.redo_button = ttk.Button(top_frame, text="Redo", command=self.redo_action, state="disabled")
        self.redo_button.pack(side=LEFT)
        self.file_label = ttk.Label(top_frame, text="No file loaded.")
        self.file_label.pack(side=LEFT, padx=10)
        
        action_frame = ttk.LabelFrame(main_frame, text="Cleaning & Actions", padding="10")
        action_frame.pack(fill=X, pady=(10, 5))
        # ... (Action frame widgets are the same, with one addition)
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
        ttk.Label(action_frame, text="Analysis:").pack(side=LEFT)
        self.plot_type_selector = ttk.Combobox(action_frame, state="readonly", width=20,
                                               values=["Histogram (Numeric)", "Bar Chart (Categorical)"])
        self.plot_type_selector.pack(side=LEFT, padx=5)
        self.plot_button = ttk.Button(action_frame, text="Generate Plot", command=self.generate_plot, bootstyle="info")
        self.plot_button.pack(side=LEFT, padx=(0,5))
        # --- NEW: Statistics Button ---
        self.stats_button = ttk.Button(action_frame, text="Show Statistics", command=self.show_statistics, bootstyle="info")
        self.stats_button.pack(side=LEFT)
        
        filter_frame = ttk.LabelFrame(main_frame, text="Filter Data", padding="10")
        filter_frame.pack(fill=X, pady=(5, 10))
        # ... (Filter frame widgets are the same)
        ttk.Label(filter_frame, text="Column:").pack(side=LEFT, padx=(0, 5))
        self.filter_column_selector = ttk.Combobox(filter_frame, state="readonly", width=15)
        self.filter_column_selector.pack(side=LEFT, padx=(0, 10))
        ttk.Label(filter_frame, text="Operator:").pack(side=LEFT, padx=(0, 5))
        self.operator_selector = ttk.Combobox(filter_frame, state="readonly", width=10,
                                              values=["==", "!=", ">", "<", ">=", "<=", "contains", "is null", "is not null"])
        self.operator_selector.pack(side=LEFT, padx=(0, 10))
        self.operator_selector.bind("<<ComboboxSelected>>", self.toggle_filter_value_entry)
        ttk.Label(filter_frame, text="Value:").pack(side=LEFT, padx=(0, 5))
        self.filter_value_entry = ttk.Entry(filter_frame, width=20)
        self.filter_value_entry.pack(side=LEFT, padx=(0, 10))
        self.apply_filter_button = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter, bootstyle="primary")
        self.apply_filter_button.pack(side=LEFT)

        bottom_pane = ttk.PanedWindow(main_frame, orient=HORIZONTAL)
        bottom_pane.pack(fill=BOTH, expand=True)
        # ... (Bottom pane is the same)
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
        history_frame = ttk.LabelFrame(bottom_pane, text="Action History", padding=5)
        self.history_text = ttk.Text(history_frame, height=10, width=40, state="disabled", wrap="word")
        self.history_text.pack(side=LEFT, fill=BOTH, expand=True)
        history_sb = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_text.yview, bootstyle="round")
        history_sb.pack(side='right', fill='y')
        self.history_text.config(yscrollcommand=history_sb.set)
        bottom_pane.add(history_frame, weight=1)

    # --- NEW: Statistics Function ---
    def show_statistics(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return
        
        try:
            stats_window = ttk.Toplevel(self)
            stats_window.title("Descriptive Statistics")
            stats_window.geometry("800x400")

            # Get statistics for all columns (numeric and object)
            stats_df = self.df.describe(include='all').round(2)
            stats_df.insert(0, 'Statistic', stats_df.index)
            
            # Create a Treeview in the new window
            stats_tree = ttk.Treeview(stats_window, show='headings', bootstyle="primary")
            stats_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

            # Setup columns
            stats_tree["column"] = list(stats_df.columns)
            for column in stats_tree["column"]:
                stats_tree.heading(column, text=column)
                stats_tree.column(column, width=100, anchor=CENTER)

            # Insert data, replacing NaN with '---' for clarity
            df_display = stats_df.replace(np.nan, '---')
            for index, row in df_display.iterrows():
                stats_tree.insert("", "end", values=list(row))

            self.log_action("Generated descriptive statistics.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate statistics: {e}")
            
    # ... (All other functions from previous step remain here unchanged) ...
    def push_to_undo(self):
        if self.df is not None:
            self.undo_stack.append(self.df.copy())
            self.update_button_states()

    def update_button_states(self):
        self.undo_button.config(state="normal" if self.undo_stack else "disabled")
        self.redo_button.config(state="normal" if self.redo_stack else "disabled")

    def undo_action(self):
        if self.undo_stack:
            self.redo_stack.append(self.df.copy())
            self.df = self.undo_stack.pop()
            self.update_treeview(self.df)
            self.log_action("Performed UNDO.")
            self.update_button_states()

    def redo_action(self):
        if self.redo_stack:
            self.undo_stack.append(self.df.copy())
            self.df = self.redo_stack.pop()
            self.update_treeview(self.df)
            self.log_action("Performed REDO.")
            self.update_button_states()

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")])
        if not filepath: return
        try:
            self.df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.update_treeview(self.df)
            self.file_label.config(text=os.path.basename(filepath))
            self.clear_history()
            self.log_action(f"Loaded {self.df.shape[0]} rows from {os.path.basename(filepath)}.")
            self.update_button_states()
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
        self.column_selector.set('')
        self.filter_column_selector['values'] = list(df.columns)
        self.filter_column_selector.set('')

    def remove_duplicates(self):
        if self.df is None: return
        original_rows = len(self.df)
        df_no_duplicates = self.df.drop_duplicates()
        rows_removed = original_rows - len(df_no_duplicates)
        if rows_removed > 0:
            self.push_to_undo()
            self.df = df_no_duplicates
            self.redo_stack.clear()
            messagebox.showinfo("Success", f"Removed {rows_removed} duplicate row(s).")
            self.log_action(f"Removed {rows_removed} duplicate row(s).")
            self.update_treeview(self.df)
            self.update_button_states()
        else:
            messagebox.showinfo("Info", "No duplicate rows found.")

    def handle_missing_values(self):
        if self.df is None: return
        column = self.column_selector.get()
        action = self.action_selector.get()
        if not column or not action: return
        self.push_to_undo()
        try:
            df_copy = self.df.copy()
            if action == "Drop Rows":
                df_copy.dropna(subset=[column], inplace=True)
            elif action in ["Fill with Mean", "Fill with Median"]:
                if not pd.api.types.is_numeric_dtype(df_copy[column]):
                    messagebox.showerror("Error", f"{action} can only be used on numeric columns.")
                    self.undo_stack.pop()
                    return
                fill_value = df_copy[column].mean() if action == "Fill with Mean" else df_copy[column].median()
                df_copy[column].fillna(fill_value, inplace=True)
            elif action == "Fill with Mode":
                df_copy[column].fillna(df_copy[column].mode()[0], inplace=True)
            elif action == "Fill with Value:":
                df_copy[column].fillna(self.custom_value_entry.get(), inplace=True)
            self.df = df_copy
            self.redo_stack.clear()
            messagebox.showinfo("Success", f"Action '{action}' applied to column '{column}'.")
            self.log_action(f"Applied '{action}' to column '{column}'.")
            self.update_treeview(self.df)
            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.undo_stack.pop()
            self.update_button_states()
            
    def apply_filter(self):
        if self.df is None: return
        column = self.filter_column_selector.get()
        operator = self.operator_selector.get()
        value = self.filter_value_entry.get()
        if not column or not operator:
            messagebox.showwarning("Input Error", "Please select a column and an operator.")
            return
        if operator not in ["is null", "is not null"] and not value:
            messagebox.showwarning("Input Error", "Please provide a value for the filter.")
            return
        self.push_to_undo()
        try:
            original_col = self.df[column]
            filtered_df = None
            if operator in [">", "<", ">=", "<="]:
                value = pd.to_numeric(value)
                col_numeric = pd.to_numeric(original_col, errors='coerce')
                if operator == ">": filtered_df = self.df[col_numeric > value]
                elif operator == "<": filtered_df = self.df[col_numeric < value]
                elif operator == ">=": filtered_df = self.df[col_numeric >= value]
                elif operator == "<=": filtered_df = self.df[col_numeric <= value]
            elif operator == "contains":
                filtered_df = self.df[original_col.astype(str).str.contains(value, case=False, na=False)]
            elif operator == "is null":
                filtered_df = self.df[original_col.isnull()]
            elif operator == "is not null":
                filtered_df = self.df[original_col.notnull()]
            else:
                try:
                    converted_value = original_col.dtype.type(value)
                    if operator == "==": filtered_df = self.df[original_col == converted_value]
                    elif operator == "!=": filtered_df = self.df[original_col != converted_value]
                except (ValueError, TypeError):
                    if operator == "==": filtered_df = self.df[original_col.astype(str) == value]
                    elif operator == "!=": filtered_df = self.df[original_col.astype(str) != value]
            self.df = filtered_df
            self.redo_stack.clear()
            self.log_action(f"Filtered column '{column}' where {operator} '{value}'.")
            self.update_treeview(self.df)
            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Filter Error", f"An error occurred during filtering: {e}")
            self.undo_stack.pop()
            self.update_button_states()
            
    def log_action(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.history_text.config(state="normal")
        self.history_text.insert(END, log_message + "\n")
        self.history_text.see(END)
        self.history_text.config(state="disabled")

    def clear_history(self):
        self.history_text.config(state="normal")
        self.history_text.delete('1.0', END)
        self.history_text.config(state="disabled")
        
    def toggle_custom_entry(self, event=None):
        if self.action_selector.get() == "Fill with Value:":
            self.custom_value_entry.config(state="normal")
        else:
            self.custom_value_entry.config(state="disabled")

    def toggle_filter_value_entry(self, event=None):
        if self.operator_selector.get() in ["is null", "is not null"]:
            self.filter_value_entry.config(state="disabled")
        else:
            self.filter_value_entry.config(state="normal")
            
    def export_to_csv(self):
        if self.df is None: return
        try:
            filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not filepath: return
            self.df.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Data successfully exported to:\n{filepath}")
            self.log_action(f"Exported data to {os.path.basename(filepath)}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {e}")

    def generate_plot(self):
        if self.df is None: return
        column = self.column_selector.get()
        plot_type = self.plot_type_selector.get()
        if not column or not plot_type: return
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
            elif plot_type == "Bar Chart (Categorical)":
                value_counts = self.df[column].value_counts().nlargest(20)
                value_counts.plot(kind='bar', ax=ax, title=f'Bar Chart of {column}')
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