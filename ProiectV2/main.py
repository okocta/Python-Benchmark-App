import re
import subprocess
import time
import tkinter as tk
from tkinter import ttk
import platform
import psutil
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import requests
import psycopg2
import platform
import psutil
import cpuinfo


def connect_db():
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="1505tavi",
            host="localhost",
            port="5432"
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
# Example GPU performance rankings (higher rank means better performance)
gpu_rankings = {
    "Intel HD Graphics 4000": 1,
    "Intel UHD Graphics 630": 2,
    "NVIDIA GeForce GT 1030": 3,
    "NVIDIA GeForce GTX 1050": 4,
    "NVIDIA GeForce GTX 1050 Ti": 5,
    "NVIDIA GeForce GTX 1060": 6,
    "NVIDIA GeForce GTX 1070": 7,
    "NVIDIA GeForce GTX 1080": 8,
    "NVIDIA GeForce RTX 2060": 9,
    "NVIDIA GeForce RTX 2070": 10,
    "NVIDIA GeForce RTX 2080": 11,
    "NVIDIA GeForce RTX 3060": 12,
    "NVIDIA GeForce RTX 3070": 13,
    "NVIDIA GeForce RTX 3080": 14,
    "NVIDIA GeForce RTX 3090": 15,
    "NVIDIA GeForce RTX 4060": 16,
    "NVIDIA GeForce RTX 4070": 17,
    "NVIDIA GeForce RTX 4080": 18,
    "NVIDIA GeForce RTX 4090": 19,
    "AMD Radeon RX 550": 3,
    "AMD Radeon RX 560": 4,
    "AMD Radeon RX 570": 5,
    "AMD Radeon RX 580": 6,
    "AMD Radeon RX 590": 7,
    "AMD Radeon RX 6600": 8,
    "AMD Radeon RX 6700 XT": 9,
    "AMD Radeon RX 6800 XT": 10,
    "AMD Radeon RX 6900 XT": 11
}


def compare_gpus(system_gpu, game_gpu):
    system_rank = gpu_rankings.get(system_gpu, 0)  # Default rank is 0 for unknown GPUs
    game_rank = gpu_rankings.get(game_gpu, 0)
    return system_rank >= game_rank
# Example CPU performance rankings
cpu_rankings = {
    "Intel Core i3": 1,
    "Intel Core i5": 2,
    "Intel Core i7": 3,
    "Intel Core i9": 4,
    "AMD Ryzen 3": 1,
    "AMD Ryzen 5": 2,
    "AMD Ryzen 7": 3,
    "AMD Ryzen 9": 4,
    "Intel Xeon": 5,
    "AMD FX": 1,
    "AMD Ryzen Threadripper": 5
}


def compare_cpus(system_cpu, game_cpu):
    system_rank = cpu_rankings.get(system_cpu, 0)  # Default rank is 0 for unknown CPUs
    game_rank = cpu_rankings.get(game_cpu, 0)
    return system_rank >= game_rank
def clean_gpu(gpu_string):
    """
    Clean and remove any 'Laptop' or 'GPU' suffix from GPU names like 'NVIDIA GeForce RTX 4060 Laptop GPU'.
    """
    # Remove the word 'Laptop' and 'GPU' from the GPU name
    cleaned_gpu = gpu_string.replace("Laptop", "").replace("GPU", "").strip()
    return cleaned_gpu


import re

def clean_cpu(cpu_string):
    """
  Clean and extract the CPU model from the full description.
  """
    # Remove unwanted characters like (R) and (TM), but keep alphanumeric and hyphen
    cpu_string = re.sub(r'\(R\)|\(TM\)', '', cpu_string)
    print(cpu_string)  # Debug print to see the cleaned string

    # Prioritize extracting "Intel Core" and subsequent words, then stop at the first number or hyphen
    match = re.search(r"Intel\s*Core\s*\w+", cpu_string, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # If "Intel Core" not found, try to extract the first two words,
    # but only if the first word is "Intel" or "AMD"
    words = cpu_string.split()
    if len(words) >= 2 and words[0] in ["Intel", "AMD"]:
        return ' '.join(words[:2])

    return "CPU model not found."



class BenchmarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Performance Benchmarking")
        self.root.geometry("1920x1080")
        self.root.configure(bg="lightgray")
        self.memory_usage_data = [0] * 60

        # Load background image for main page and other sections
        self.main_bg = Image.open("background-image.jpg")
        self.main_bg_image = ImageTk.PhotoImage(self.main_bg)

        self.system_info_bg = Image.open("background-image.jpg")
        self.system_info_bg_image = ImageTk.PhotoImage(self.system_info_bg)

        self.cpu_bg = Image.open("background-image.jpg")
        self.cpu_bg_image = ImageTk.PhotoImage(self.cpu_bg)

        self.memory_bg = Image.open("background-image.jpg")
        self.memory_bg_image = ImageTk.PhotoImage(self.memory_bg)

        self.disk_bg = Image.open("background-image.jpg")
        self.disk_bg_image = ImageTk.PhotoImage(self.disk_bg)

        self.gpu_bg = Image.open("background-image.jpg")
        self.gpu_bg_image = ImageTk.PhotoImage(self.gpu_bg)

        self.cyri_bg = Image.open("background-image.jpg")
        self.cyri_bg_image = ImageTk.PhotoImage(self.cyri_bg)

        # Frame for the main page
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill="both", expand=True)

        # Set the background image for the main frame
        self.main_background_label = tk.Label(self.main_frame, image=self.main_bg_image)
        self.main_background_label.place(relwidth=1, relheight=1)

        self.last_disk_io = psutil.disk_io_counters()
        self.last_update_time = time.time()

        # Create buttons for each section
        self.create_buttons()

    def create_buttons(self):
        # Style for the buttons
        style = ttk.Style()
        style.configure("TButton",
                        font=("Arial", 14),
                        padding=10,
                        width=20,
                        relief="flat",
                        background="#4CAF50",
                        foreground="Black")
        style.map("TButton", background=[("active", "#45a049")])

        # Create buttons for each section
        system_info_button = ttk.Button(self.main_frame, text="System Info", command=self.show_system_info)
        system_info_button.pack(pady=20)

        cpu_button = ttk.Button(self.main_frame, text="CPU Info", command=self.show_cpu_info)
        cpu_button.pack(pady=20)

        memory_button = ttk.Button(self.main_frame, text="Memory Info", command=self.show_memory_info)
        memory_button.pack(pady=20)

        disk_button = ttk.Button(self.main_frame, text="Disk Info", command=self.show_disk_info)
        disk_button.pack(pady=20)

        gpu_button = ttk.Button(self.main_frame, text="GPU Info", command=self.show_gpu_info)
        gpu_button.pack(pady=20)

        cyri_button = ttk.Button(self.main_frame, text="Can You Run It", command=self.show_cyri_info)
        cyri_button.pack(pady=20)

    def create_back_button(self, frame):
        back_button = ttk.Button(frame, text="Back", command=self.show_main_page)
        back_button.pack(pady=20)

    def show_main_page(self):
        self.clear_frame()
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill="both", expand=True)

        # Set the background image for the main frame
        self.main_background_label = tk.Label(self.main_frame, image=self.main_bg_image)
        self.main_background_label.place(relwidth=1, relheight=1)

        self.create_buttons()

    def show_system_info(self):
        self.clear_frame()
        system_info_frame = tk.Frame(self.root)
        system_info_frame.pack(fill="both", expand=True)

        # Set the background image for this section
        system_info_background_label = tk.Label(system_info_frame, image=self.system_info_bg_image)
        system_info_background_label.place(relwidth=1, relheight=1)

        system_info = platform.uname()
        system_info_text = f"""
        System: {system_info.system}
        Node Name: {system_info.node}
        Release: {system_info.release}
        Version: {system_info.version}
        Machine: {system_info.machine}
        Processor: {system_info.processor}
        """
        info_label = ttk.Label(system_info_frame, text=system_info_text, style="TLabel", justify="left",background="grey14",foreground="white",font=("Arial", 13, "bold"))
        info_label.pack(pady=10)

        # Add back button
        self.create_back_button(system_info_frame)

    def show_cpu_info(self):
        self.clear_frame()
        cpu_frame = tk.Frame(self.root)
        cpu_frame.pack(fill="both", expand=True)

        # Set the background image for this section
        cpu_background_label = tk.Label(cpu_frame, image=self.cpu_bg_image)
        cpu_background_label.place(relwidth=1, relheight=1)

        # CPU info text
        cpu_info=cpuinfo.get_cpu_info()['brand_raw']
        cpu_count = psutil.cpu_count(logical=False)
        logical_cpu_count = psutil.cpu_count(logical=True)
        cpu_info_text = f"""
        Processor: {cpu_info}
        Physical Cores: {cpu_count}
        Logical Cores: {logical_cpu_count}
        """
        info_label = ttk.Label(cpu_frame, text=cpu_info_text, style="TLabel", justify="left",background="grey14",foreground="white",font=("Arial", 13, "bold"))
        info_label.pack(pady=10)

        # Set up figure for CPU usage graph
        self.cpu_fig = Figure(figsize=(6, 2), dpi=100)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_ylabel("CPU Usage (%)")
        self.cpu_ax.set_xticks([])

        self.cpu_usage_data = [0] * 60

        # Add the CPU usage graph below the CPU info text
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, cpu_frame)
        self.cpu_canvas.get_tk_widget().pack()

        # Create label for CPU speed
        self.cpu_speed_label = ttk.Label(cpu_frame, text="CPU Speed: Loading...", background="grey14",foreground="white",font=("Arial", 13, "bold"),style="TLabel", justify="left")
        self.cpu_speed_label.pack(pady=10)

        # Start updating the CPU usage graph
        self.update_cpu_usage(cpu_frame)

        # Add back button
        self.create_back_button(cpu_frame)

    def update_cpu_usage(self, cpu_frame):
        # Update CPU usage graph and speed display
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq().current  # Get current CPU frequency (MHz)

        self.cpu_usage_data.append(cpu_usage)
        self.cpu_usage_data = self.cpu_usage_data[1:]

        self.cpu_ax.clear()
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.plot(self.cpu_usage_data, color="green")
        self.cpu_ax.set_title(f"CPU Usage: {cpu_usage:.1f}%")
        self.cpu_canvas.draw()

        # Update CPU speed display
        self.cpu_speed_label.config(text=f"CPU Speed: {cpu_freq} MHz")

        # Continue updating the CPU usage every second
        self.root.after(1000, self.update_cpu_usage, cpu_frame)

    def show_memory_info(self):
        self.clear_frame()
        memory_frame = tk.Frame(self.root)
        memory_frame.pack(fill="both", expand=True)

        # Set the background image for this section
        memory_background_label = tk.Label(memory_frame, image=self.memory_bg_image)
        memory_background_label.place(relwidth=1, relheight=1)

        # Create label for memory info
        self.memory_info_label = ttk.Label(memory_frame, text="Loading Memory Info...", style="TLabel", justify="left",background="grey14",foreground="white",font=("Arial", 13, "bold"))
        self.memory_info_label.pack(pady=10)

        # Set up figure for Memory usage graph
        self.memory_fig = Figure(figsize=(6, 2), dpi=100)
        self.memory_ax = self.memory_fig.add_subplot(111)
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.set_ylabel("Memory Usage (%)")
        self.memory_ax.set_xticks([])

        # Add the Memory usage graph below the Memory info text
        self.memory_canvas = FigureCanvasTkAgg(self.memory_fig, memory_frame)
        self.memory_canvas.get_tk_widget().pack(pady=20)

        # Start updating the Memory usage graph
        self.update_memory_usage(memory_frame)

        # Add back button
        self.create_back_button(memory_frame)

    def update_memory_usage(self, memory_frame):
        # Update Memory usage graph and display
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        self.memory_usage_data.append(memory_usage)
        self.memory_usage_data = self.memory_usage_data[1:]

        self.memory_ax.clear()
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.plot(self.memory_usage_data, color="blue")
        self.memory_ax.set_title(f"Memory Usage: {memory_usage}%")
        self.memory_canvas.draw()

        # Update memory info label
        memory_info_text = f"""
        Total Memory: {memory.total / (1024 ** 3):.2f} GB
        Used Memory: {memory.used / (1024 ** 3):.2f} GB
        Free Memory: {memory.available / (1024 ** 3):.2f} GB
        """
        self.memory_info_label.config(text=memory_info_text)

        # Continue updating the Memory usage every second
        self.root.after(1000, self.update_memory_usage, memory_frame)


    def show_disk_info(self):
        self.clear_frame()
        disk_frame = tk.Frame(self.root)
        disk_frame.pack(fill="both", expand=True)

        # Set the background image for the disk tab section
        disk_background_label = tk.Label(disk_frame, image=self.disk_bg_image)
        disk_background_label.place(relwidth=1, relheight=1)

        # Create label for disk info
        self.disk_info_label = ttk.Label(disk_frame, text="Loading Disk Info...", style="TLabel", justify="left",background="grey14",foreground="white",font=("Arial", 13, "bold"))
        self.disk_info_label.pack(pady=10)

        # Set up figure for Active Time and Transfer Rate graphs
        fig, (self.ax_active, self.ax_transfer) = plt.subplots(2, 1, figsize=(6, 4))
        fig.subplots_adjust(hspace=0.5)

        # Set up the graphs with labels
        self.ax_active.set_title("Active Time")
        self.ax_active.set_ylim(0, 100)
        self.ax_active.set_xlim(0, 60)  # 60 seconds
        self.active_data = [0] * 60  # Store 60 seconds of data

        self.ax_transfer.set_title("Disk Transfer Rate")
        self.ax_transfer.set_ylim(0, 10)  # Example max 10 MB/s
        self.ax_transfer.set_ylabel("MB/s")
        self.ax_transfer.set_xlim(0, 60)
        self.transfer_data = [0] * 60

        # Set up line objects for updating in the animation
        self.line_active, = self.ax_active.plot(self.active_data, color="green")
        self.line_transfer, = self.ax_transfer.plot(self.transfer_data, color="green")

        # Create a canvas to show the Matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=disk_frame)
        self.canvas.get_tk_widget().pack()

        # Start updating the disk usage info and graph in real time
        self.update_disk_info()
        self.anim = FuncAnimation(fig, self.update_graph, interval=1000, save_count=60)  # Limit cache to 60 frames

        # Add back button
        self.create_back_button(disk_frame)

    def update_disk_info(self):
        # Get disk usage details
        disk_usage = psutil.disk_usage('/')
        total_disk_capacity = disk_usage.total / (1024 ** 3)  # Convert to GB
        used_disk_space = disk_usage.used / (1024 ** 3)  # Convert to GB
        free_disk_space = disk_usage.free / (1024 ** 3)  # Convert to GB

        # Get the current disk I/O counters
        current_disk_io = psutil.disk_io_counters()
        current_time = time.time()
        delta_time = current_time - self.last_update_time

        # Ensure delta_time is not too small (avoid division by zero or very small values)
        if delta_time > 0:
            # Calculate the rate of read and write bytes per second
            read_bytes_rate = (current_disk_io.read_bytes - self.last_disk_io.read_bytes) / delta_time
            write_bytes_rate = (current_disk_io.write_bytes - self.last_disk_io.write_bytes) / delta_time

            # Update transfer data for the graph (in MB/s)
            self.transfer_data.append((read_bytes_rate + write_bytes_rate) / (1024 * 1024))
            self.transfer_data = self.transfer_data[1:]

            # Calculate disk active time percentage based on read and write times
            active_time_ms = current_disk_io.read_time + current_disk_io.write_time - \
                             self.last_disk_io.read_time - self.last_disk_io.write_time
            active_percentage = (active_time_ms / (
                        delta_time * 1000)) * 100  # Convert ms to seconds, then to percentage
        else:
            active_percentage = 0

        # Update the last disk I/O data and timestamp for the next calculation
        self.last_disk_io = current_disk_io
        self.last_update_time = current_time

        # Display disk usage, capacity, and read/write information
        disk_info_text = f"""
        Disk Usage: {disk_usage.percent}%
        Total Capacity: {total_disk_capacity:.2f} GB
        Used Space: {used_disk_space:.2f} GB
        Free Space: {free_disk_space:.2f} GB
        Read Speed: {read_bytes_rate / (1024 * 1024):.2f} MB/s
        Write Speed: {write_bytes_rate / (1024 * 1024):.2f} MB/s
        """
        self.disk_info_label.config(text=disk_info_text)

        # Schedule the next update
        self.root.after(1000, self.update_disk_info)

    def update_graph(self, i):
        # Retrieve the latest disk I/O data
        current_disk_io = psutil.disk_io_counters()
        current_time = time.time()
        delta_time = current_time - self.last_update_time

        # Calculate the active time percentage
        if delta_time > 0:
            # Compute the percentage of time spent on read/write operations over the last interval
            active_time_ms = current_disk_io.read_time + current_disk_io.write_time - \
                             self.last_disk_io.read_time - self.last_disk_io.write_time
            active_percentage = (active_time_ms / (
                        delta_time * 1000)) * 100  # Convert ms to seconds, then to percentage
        else:
            active_percentage = 0

        # Append and trim the active time data for the graph
        self.active_data.append(active_percentage)
        self.active_data = self.active_data[1:]

        # Calculate transfer rate for the transfer rate graph
        transfer_rate = (current_disk_io.read_bytes + current_disk_io.write_bytes -
                         self.last_disk_io.read_bytes - self.last_disk_io.write_bytes) / delta_time / (1024 * 1024)
        self.transfer_data.append(transfer_rate)
        self.transfer_data = self.transfer_data[1:]

        # Update the active time graph
        self.line_active.set_ydata(self.active_data)
        self.ax_active.set_ylim(0, 100)
        self.ax_active.set_xlim(0, 60)

        # Update the title of the active time graph to reflect the latest active time percentage
        self.ax_active.set_title(f"Active Time: {active_percentage:.1f}%")

        # Update the transfer rate graph
        self.line_transfer.set_ydata(self.transfer_data)
        self.ax_transfer.set_ylim(0, max(self.transfer_data) * 1.2)
        self.ax_transfer.set_xlim(0, 60)

        # Redraw the canvas to show updated titles and data
        self.canvas.draw()

        # Update last disk IO counters and time for the next calculation
        self.last_disk_io = current_disk_io
        self.last_update_time = current_time

    def show_gpu_info(self):
        # Clear previous frame content
        self.clear_frame()

        # Create the GPU frame
        gpu_frame = tk.Frame(self.root)
        gpu_frame.pack(fill="both", expand=True)

        # Set the background image for this section
        gpu_background_label = tk.Label(gpu_frame, image=self.gpu_bg_image)
        gpu_background_label.place(relwidth=1, relheight=1)

        # GPU info label
        self.gpu_info_label = ttk.Label(gpu_frame, text="Loading GPU Info...", style="TLabel", justify="left",background="grey14",foreground="white",font=("Arial", 13, "bold"))
        self.gpu_info_label.pack(pady=10)

        # Create a figure for GPU load and memory usage graphs
        self.gpu_fig, (self.ax_gpu_load, self.ax_gpu_memory) = plt.subplots(2, 1, figsize=(6, 4))
        self.gpu_fig.subplots_adjust(hspace=0.5)

        # Set up GPU load graph
        self.ax_gpu_load.set_title("GPU Load (%)")
        self.ax_gpu_load.set_ylim(0, 100)
        self.ax_gpu_load.set_xlim(0, 60)  # 60 seconds of data
        self.gpu_load_data = [0] * 60

        # Set up GPU memory usage graph
        self.ax_gpu_memory.set_title("GPU Memory Usage (MB)")
        self.ax_gpu_memory.set_ylim(0, 10000)  # Max GPU memory (in MB)
        self.ax_gpu_memory.set_xlim(0, 60)  # 60 seconds of data
        self.gpu_memory_data = [0] * 60

        # Create a canvas for displaying the Matplotlib figure
        self.gpu_canvas = FigureCanvasTkAgg(self.gpu_fig, master=gpu_frame)
        self.gpu_canvas.get_tk_widget().pack(pady=20)

        # Fetch GPU info and update labels
        self.update_gpu_info()

        # Add a back button
        self.create_back_button(gpu_frame)

        # Start an animation to update GPU data every second
        self.gpu_anim = FuncAnimation(self.gpu_fig, self.update_gpu_graph, interval=1000, save_count=60)
    def get_gpu_info(self):
        try:
            output = subprocess.check_output(
                ['nvidia-smi',
                 '--query-gpu=index,name,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu',
                 '--format=csv,noheader,nounits'], encoding='utf-8')
            gpus = []
            for line in output.strip().split('\n'):
                index, name, driver_version, memory_total, memory_used, memory_free, utilization_gpu, temperature_gpu = line.split(
                    ', ')
                gpus.append({
                    'id': int(index),
                    'name': name,
                    'driver': driver_version,
                    'memoryTotal': int(memory_total),
                    'memoryUsed': int(memory_used),
                    'memoryFree': int(memory_free),
                    'load': float(utilization_gpu),
                    'temperature': int(temperature_gpu)
                })
            if not gpus:
                print("No GPUs detected.")
            return gpus
        except subprocess.CalledProcessError as e:
            print(f"Error executing nvidia-smi: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while getting GPU information: {e}")
            return []
    def update_gpu_info(self):
        gpus = self.get_gpu_info()
        if gpus:
            gpu_info_text = ""
            for gpu in gpus:
                gpu_info_text += f"""
                Name: {gpu['name']}
                Driver Version: {gpu['driver']}
                Total Memory: {gpu['memoryTotal']} MB
                Used Memory: {gpu['memoryUsed']} MB
                Free Memory: {gpu['memoryFree']} MB
                Load: {gpu['load']}%
                Temperature: {gpu['temperature']}°C
                \n"""  # Adds line breaks between GPUs
            # Ensure gpu_info_label exists before updating
            try:
                self.gpu_info_label.config(text=gpu_info_text,background="grey14",foreground="white",font=("Arial", 9, "bold"))
            except tk.TclError:
                print("Error: gpu_info_label is no longer available.")
                return
        else:
            try:
                self.gpu_info_label.config(text="No GPU detected",background="grey14",foreground="white",font=("Arial", 13, "bold"))
            except tk.TclError:
                print("Error: gpu_info_label is no longer available.")
                return
        # Continue updating GPU info every second
        self.root.after(1000, self.update_gpu_info)
    def update_gpu_graph(self, i):
        # Get GPU data and update the graphs
        gpus = self.get_gpu_info()
        if gpus:
            for gpu in gpus:
                # Update GPU Load graph
                self.gpu_load_data.append(gpu['load'])
                self.gpu_load_data = self.gpu_load_data[1:]
                # Update GPU Memory Usage graph
                self.gpu_memory_data.append(gpu['memoryUsed'])
                self.gpu_memory_data = self.gpu_memory_data[1:]
            # Update GPU Load graph
            self.ax_gpu_load.clear()
            self.ax_gpu_load.set_ylim(0, 100)
            self.ax_gpu_load.set_xlim(0, 60)
            self.ax_gpu_load.plot(self.gpu_load_data, color="green")
            self.ax_gpu_load.set_title(f"GPU Load: {gpus[0]['load']}%")
            # Update GPU Memory Usage graph
            self.ax_gpu_memory.clear()
            if self.gpu_memory_data:
                self.ax_gpu_memory.set_ylim(0, max(self.gpu_memory_data) * 1.2)
            else:
                self.ax_gpu_memory.set_ylim(0, 100)  # Set a default range if no data
            self.ax_gpu_memory.set_xlim(0, 60)
            self.ax_gpu_memory.plot(self.gpu_memory_data, color="blue")
            self.ax_gpu_memory.set_title(f"GPU Memory Used: {gpus[0]['memoryUsed']} MB")
            # Redraw the canvas with updated data
            self.gpu_canvas.draw()

    def show_cyri_info(self):
        """
        Display the 'Can You Run It' section with input fields, system specs, game requirements, and results.
        """
        self.clear_frame()  # Clear existing frame
        cyri_frame = tk.Frame(self.root)
        cyri_frame.pack(fill="both", expand=True)

        # Set the background image for this section
        if self.cyri_bg_image:
            cyri_background_label = tk.Label(cyri_frame, image=self.cyri_bg_image)
            cyri_background_label.place(relwidth=1, relheight=1)

        # Title
        cyri_info_label = ttk.Label(
            cyri_frame, text="Can You Run It?", style="TLabel",
            background="grey14", foreground="white", font=("Arial", 13, "bold")
        )
        cyri_info_label.pack(pady=10)

        # Display System Specs on load
        system_specs = self.get_system_specs()
        system_specs_text = (
            f"CPU: {system_specs['cpu']}\n"
            f"GPU: {system_specs['gpu']}\n"
            f"RAM: {system_specs['ram']}\n"
            f"Storage: {system_specs['storage']}"
        )
        ttk.Label(
            cyri_frame, text="Your System Specs:", style="TLabel",
            background="grey14", foreground="white", font=("Arial", 11, "bold")
        ).pack(pady=5)
        self.system_specs_label = ttk.Label(
            cyri_frame, text=system_specs_text, style="TLabel",
            background="grey14", foreground="white", font=("Arial", 11), justify="left"
        )
        self.system_specs_label.pack(pady=10)

        # Game Name Entry with Dropdown Search
        ttk.Label(
            cyri_frame, text="Enter the Game Name:",
            background="grey14", foreground="white", font=("Arial", 13, "bold"), style="TLabel"
        ).pack(pady=5)

        self.game_name_entry = ttk.Entry(cyri_frame)
        self.game_name_entry.pack(pady=10)
        self.game_name_entry.bind('<KeyRelease>', self.update_dropdown)  # Bind key release event to update dropdown

        # Dropdown List
        self.game_listbox = tk.Listbox(cyri_frame, height=5, font=("Arial", 11))
        self.game_listbox.pack(pady=10)
        self.game_listbox.bind('<<ListboxSelect>>', self.select_game_from_list)

        # Check button to trigger system requirements check
        check_button = ttk.Button(cyri_frame, text="Check Requirements", command=self.check_game_requirements)
        check_button.pack(pady=10)

        # Section for displaying game requirements
        self.game_requirements_label = ttk.Label(
            cyri_frame, text="Minimum Requirements: Waiting for input...", style="TLabel",
            background="grey14", foreground="white", font=("Arial", 11, "bold"), justify="left"
        )
        self.game_requirements_label.pack(pady=10)

        # Label to display result
        self.cyri_result_label = ttk.Label(
            cyri_frame, text="", style="TLabel",
            background="grey14", font=("Arial", 13, "bold")
        )
        self.cyri_result_label.pack(pady=10)

        # Back button
        self.create_back_button(cyri_frame)

    def update_dropdown(self, event):
        """
        Update the dropdown list based on the current input in the game_name_entry field.
        """
        search_query = self.game_name_entry.get()
        if len(search_query) >= 3:
            connection = connect_db()  # Connect to the database
            if connection:
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT game_name FROM game_requirements WHERE game_name ILIKE %s LIMIT 10",
                                   (f"{search_query}%",))
                    games = cursor.fetchall()
                    self.game_listbox.delete(0, tk.END)  # Clear the listbox
                    for game in games:
                        self.game_listbox.insert(tk.END, game[0])  # Add games to the listbox
                except Exception as e:
                    print(f"Error fetching game names: {e}")
                finally:
                    cursor.close()
                    connection.close()
        else:
            self.game_listbox.delete(0, tk.END)  # Clear the listbox if input is less than 3 characters

    def select_game_from_list(self, event):
        """
        Handle game selection from the listbox and update the entry field with the selected game.
        """
        selected_game = self.game_listbox.get(self.game_listbox.curselection())
        self.game_name_entry.delete(0, tk.END)  # Clear the entry field
        self.game_name_entry.insert(0, selected_game)  # Set the selected game name

    def get_game_system_requirements(self, game_name):
        """
        Fetch the system requirements for the specified game from the database.
        """
        connection = connect_db()
        if not connection:
            print("Database connection failed.")
            return None

        cursor = connection.cursor()
        try:
            query = "SELECT cpu, gpu, ram, storage FROM game_requirements WHERE game_name = %s"
            cursor.execute(query, (game_name,))
            game_info = cursor.fetchone()

            if game_info:
                return {
                    "cpu": game_info[0],
                    "gpu": game_info[1],
                    "ram": game_info[2],
                    "storage": game_info[3]
                }
            else:
                print(f"No requirements found for {game_name}")
                return None
        except Exception as e:
            print(f"Error fetching data for {game_name}: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    def get_system_specs(self):
        """
        Dynamically fetch the system specifications.
        """
        # Fetch CPU details
        cpu=cpuinfo.get_cpu_info()['brand_raw']
        cpu = clean_cpu(cpu)

        # Fetch GPU details
        gpu_info = self.get_gpu_info()
        if gpu_info:
            gpu = clean_gpu(gpu_info[0]['name'])  # Clean the GPU name (e.g., remove "Laptop GPU")
        else:
            gpu = "No GPU detected or unsupported GPU"

        # Fetch total RAM and storage
        ram = f"{round(psutil.virtual_memory().total / (1024 ** 3))} GB"
        storage = f"{round(psutil.disk_usage('/').total / (1024 ** 3))} GB"

        return {
            "cpu": cpu,
            "gpu": gpu,
            "ram": ram,
            "storage": storage
        }

    def check_game_requirements(self):
        """
        Check if the current system meets the requirements for the specified game.
        """
        game_name = self.game_name_entry.get()
        print(f"Checking requirements for: {game_name}")

        # Fetch game requirements from the database
        game_info = self.get_game_system_requirements(game_name)
        if not game_info:
            self.cyri_result_label.config(
                text="Game not found in the database.", foreground="red"
            )
            return

        print(f"Game Requirements: {game_info}")

        # Fetch system specs dynamically
        system_specs = self.get_system_specs()
        print(f"System Specs: {system_specs}")

        # Display system specs and game requirements
        system_specs_text = (
            f"CPU: {system_specs['cpu']}\n"
            f"GPU: {system_specs['gpu']}\n"
            f"RAM: {system_specs['ram']}\n"
            f"Storage: {system_specs['storage']}"
        )
        self.system_specs_label.config(text=f"System Specs:\n{system_specs_text}")

        game_requirements_text = (
            f"CPU: {game_info['cpu']}\n"
            f"GPU: {game_info['gpu']}\n"
            f"RAM: {game_info['ram']}\n"
            f"Storage: {game_info['storage']}"
        )
        self.game_requirements_label.config(text=f"Minimum Requirements:\n{game_requirements_text}")

        # Extract numeric values for RAM and storage
        def extract_numeric(value):
            import re
            match = re.search(r'\d+', value)
            return int(match.group()) if match else 0

        system_ram = extract_numeric(system_specs["ram"])
        game_ram = extract_numeric(game_info["ram"])
        system_storage = extract_numeric(system_specs["storage"])
        game_storage = extract_numeric(game_info["storage"])

        # Compare specs
        cpu_check = compare_cpus(system_specs["cpu"], game_info["cpu"])
        gpu_check = compare_gpus(system_specs["gpu"], game_info["gpu"])
        ram_check = system_ram >= game_ram
        storage_check = system_storage >= game_storage

        # Debugging output
        print(f"CPU Check: {cpu_check}, GPU Check: {gpu_check}, RAM Check: {ram_check}, Storage Check: {storage_check}")

        # Set result label based on the comparison
        if cpu_check and gpu_check and ram_check and storage_check:
            self.cyri_result_label.config(
                text="Your system meets the game's requirements!", foreground="green"
            )
        else:
            self.cyri_result_label.config(
                text="Your system does not meet the game's requirements.", foreground="red"
            )

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BenchmarkApp(root)
    root.mainloop()
