import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# 🔧 **Configurable Variables** (Change These Easily)
DEPTH_CSV = "_bluerov2_global_position_rel_alt.csv"  # Path to depth CSV
COMMAND_CSV = "_bluerov2_rc_override.csv"  # Path to command CSV
LINE_WIDTH = 2  # Set line thickness
LEGEND_POSITION = "lower right"  # Position of legend
X_LABEL = "Time (s)"  # X-axis label

# Function to parse space-separated command channel data
def parse_channels(channel_str):
    try:
        numbers = re.findall(r"[-+]?[0-9]*\.?[0-9]+", channel_str)  # Extract numbers from space-separated format
        return np.array([int(num) for num in numbers])  # Convert to integer array
    except (ValueError, SyntaxError):
        return np.zeros(18)  # Default to an array of zeros

# Load and preprocess depth data
def load_depth_data(csv_file):
    df = pd.read_csv(csv_file)
    df["Time"] = (df["timestamp"] - df["timestamp"].min()) / 1e9  # Convert timestamp to seconds
    return df

# Load and preprocess command data
def load_command_data(csv_file):
    df = pd.read_csv(csv_file)
    df["Time"] = (df["timestamp"] - df["timestamp"].min()) / 1e9  # Convert timestamp to seconds
    df["_channels"] = df["_channels"].apply(parse_channels)  # Convert space-separated string to array
    return df

# Plot depth and command values with dual Y-axes
def plot_depth_and_command(depth_df, command_df):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Primary y-axis for Depth
    color = 'tab:blue'
    ax1.set_xlabel(X_LABEL, fontsize=20)
    ax1.set_ylabel("Depth (m)", fontsize=20, color=color)
    ax1.plot(depth_df["Time"], depth_df["_data"], label="Depth", linewidth=LINE_WIDTH, linestyle='dashed', color=color)
    ax1.tick_params(axis='y', labelcolor=color, labelsize=20)
    ax1.tick_params(axis='both', labelsize=20)
    
    # Secondary y-axis for Command Channel 3
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel("Command Channel 3", fontsize=20, color=color)
    ax2.plot(command_df["Time"], command_df["_channels"].apply(lambda x: x[2]), label="Command Channel 3", linewidth=LINE_WIDTH, color=color)
    ax2.tick_params(axis='y', labelcolor=color, labelsize=20)
    ax2.tick_params(axis='both', labelsize=20)
    
    # ✅ **Grid and Layout Adjustments**
    ax1.grid(True)
    plt.tight_layout()
    plt.savefig("1_2st_plot.pdf", format='pdf')
    plt.show()

# 🚀 **Run the Script**
depth_df = load_depth_data(DEPTH_CSV)
command_df = load_command_data(COMMAND_CSV)
plot_depth_and_command(depth_df, command_df)
