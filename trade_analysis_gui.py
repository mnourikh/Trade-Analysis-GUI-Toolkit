
# Trade Analysis Toolkit with GUI
# This script provides a GUI for trade data analysis using tkinter.

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tkinter import Tk, filedialog, Label, Button, messagebox
from tkinter.ttk import Combobox

# Core Analysis Functions
def aggregate_and_scale(df, code_column='Code', scaler=None):
    df = df.groupby(['year', 'month', code_column]).agg({
        'weight': 'sum',
        'rial': 'sum',
        'dollar': 'sum'
    }).reset_index()

    if scaler is None:
        scaler = MinMaxScaler()

    df[['weight_scaled', 'rial_scaled', 'dollar_scaled']] = scaler.fit_transform(
        df[['weight', 'rial', 'dollar']]
    )
    return df

def calculate_volatility(df, column='dollar', name='Volatility', code_column='Code'):
    df[column] = df[column].replace(0, np.nan)
    df[name] = df.groupby(code_column)[column].apply(lambda x: np.log(x).diff())
    df[name].replace([np.inf, -np.inf], np.nan, inplace=True)
    return df

def export_to_excel(dfs, output_path):
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for sheet_name, df in dfs.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Results saved to {output_path}")

# GUI Implementation
class TradeAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trade Analysis Toolkit")

        # File paths
        self.export_file = None
        self.import_file = None

        # Labels and Buttons
        Label(root, text="Trade Analysis Toolkit", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        Button(root, text="Load Export Data", command=self.load_export_data).grid(row=1, column=0, padx=10, pady=5)
        Button(root, text="Load Import Data", command=self.load_import_data).grid(row=1, column=1, padx=10, pady=5)

        self.export_label = Label(root, text="No Export Data Loaded", fg="red")
        self.export_label.grid(row=2, column=0, padx=10, pady=5)

        self.import_label = Label(root, text="No Import Data Loaded", fg="red")
        self.import_label.grid(row=2, column=1, padx=10, pady=5)

        Button(root, text="Run Analysis", command=self.run_analysis).grid(row=3, column=0, columnspan=2, pady=10)

    def load_export_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Parquet Files", "*.parquet")])
        if file_path:
            self.export_file = file_path
            self.export_label.config(text="Export Data Loaded", fg="green")
            print(f"Export file loaded: {file_path}")

    def load_import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Parquet Files", "*.parquet")])
        if file_path:
            self.import_file = file_path
            self.import_label.config(text="Import Data Loaded", fg="green")
            print(f"Import file loaded: {file_path}")

    def run_analysis(self):
        if not self.export_file or not self.import_file:
            messagebox.showerror("Error", "Please load both Export and Import data files.")
            return

        # Load data
        export_data = pd.read_parquet(self.export_file)
        import_data = pd.read_parquet(self.import_file)

        # Perform analysis
        export_scaled = aggregate_and_scale(export_data, code_column='Code')
        import_scaled = aggregate_and_scale(import_data, code_column='Code')
        export_volatility = calculate_volatility(export_scaled, column='dollar', name='Volatility')
        import_volatility = calculate_volatility(import_scaled, column='dollar', name='Volatility')

        # Save results
        output_file = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Excel Files", "*.xlsx")],
                                                   title="Save Analysis Results")
        if output_file:
            results = {
                "Export Data": export_scaled,
                "Export Volatility": export_volatility,
                "Import Data": import_scaled,
                "Import Volatility": import_volatility,
            }
            export_to_excel(results, output_file)
            messagebox.showinfo("Success", f"Results saved to {output_file}")

if __name__ == "__main__":
    root = Tk()
    app = TradeAnalysisGUI(root)
    root.mainloop()
