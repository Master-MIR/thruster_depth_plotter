import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# Configurable variables
LINE_WIDTH = 2  # Set line thickness
X_LABEL = "Time (s)"  # X-axis label
DEPTH_CSV_NAME = "_bluerov2_global_position_rel_alt.csv"
COMMAND_CSV_NAME = "_bluerov2_rc_override.csv"
SMOOTHING_WINDOW = 5  # Adjust the size of the moving average window

def parse_channels(channel_str):
    """Parse space-separated command channel data into an array."""
    try:
        numbers = re.findall(r"[-+]?[0-9]*\.?[0-9]+", channel_str)
        return np.array([int(num) for num in numbers])
    except (ValueError, SyntaxError):
        return np.zeros(18)

def pwm_to_force(pwm):
    """Convert PWM value to force using the inverse of the given equation."""
    return (1468 - pwm) / 11

def smooth_data(data, window=SMOOTHING_WINDOW):
    """Apply a simple moving average to smooth the data."""
    return data.rolling(window=window, center=True).mean()

def load_depth_data(csv_file):
    """Load and preprocess depth data from CSV."""
    df = pd.read_csv(csv_file)
    df["Time"] = (df["timestamp"] - df["timestamp"].min()) / 1e9
    df["_data"] = smooth_data(df["_data"])  # Apply smoothing
    return df

def load_command_data(csv_file):
    """Load and preprocess command data from CSV, converting PWM to force."""
    df = pd.read_csv(csv_file)
    df["Time"] = (df["timestamp"] - df["timestamp"].min()) / 1e9
    df["_channels"] = df["_channels"].apply(parse_channels)
    df["Force"] = df["_channels"].apply(lambda x: pwm_to_force(x[2]))
    df["Force"] = smooth_data(df["Force"])  # Apply smoothing
    return df

def plot_depth_and_force(depth_df, command_df, save_path):
    """Generate and save a plot of depth and force data."""
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Primary y-axis for Depth
    color = 'tab:blue'
    ax1.set_xlabel(X_LABEL, fontsize=18)
    ax1.set_ylabel("Depth (m)", fontsize=18, color=color, labelpad=10)
    depth_line, = ax1.plot(depth_df["Time"], depth_df["_data"], label="Depth", linewidth=LINE_WIDTH, linestyle='dashed', color=color)
    ax1.tick_params(axis='y', labelcolor=color, labelsize=14)
    ax1.tick_params(axis='both', labelsize=14)
    
    # Secondary y-axis for Force
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel("Force", fontsize=18, color=color, labelpad=10)
    force_line, = ax2.plot(command_df["Time"], command_df["Force"], label="Force", linewidth=LINE_WIDTH, color=color)
    ax2.tick_params(axis='y', labelcolor=color, labelsize=14)
    ax2.tick_params(axis='both', labelsize=14)
    
    # Adjusted legend placement to avoid overlap
    lines = [depth_line, force_line]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="lower right", fontsize=14)
    
    # Grid and Layout Adjustments
    ax1.grid(True)
    plt.tight_layout()
    
    # Save plot
    plt.savefig(save_path, format='pdf')
    plt.close()
    print(f"Saved plot: {save_path}")

def find_folders_with_csv(base_dir):
    """Finds all subdirectories containing both required CSV files."""
    valid_folders = []
    for root, _, files in os.walk(base_dir):
        if DEPTH_CSV_NAME in files and COMMAND_CSV_NAME in files:
            valid_folders.append(root)
    return valid_folders

def process_all_folders(base_dir):
    """Processes all folders with CSV files and generates corresponding plots."""
    folders = find_folders_with_csv(base_dir)

    for folder in folders:
        depth_csv_path = os.path.join(folder, DEPTH_CSV_NAME)
        command_csv_path = os.path.join(folder, COMMAND_CSV_NAME)
        folder_name = os.path.basename(folder)  # Extract folder name
        plot_save_path = os.path.join(folder, f"{folder_name}_force.pdf")  # Name the PDF after the folder

        try:
            depth_df = load_depth_data(depth_csv_path)
            command_df = load_command_data(command_csv_path)
            plot_depth_and_force(depth_df, command_df, plot_save_path)
        except Exception as e:
            print(f"Error processing folder {folder}: {e}")

if __name__ == '__main__':
    base_directory = os.getcwd()  # Change this if needed
    process_all_folders(base_directory)
