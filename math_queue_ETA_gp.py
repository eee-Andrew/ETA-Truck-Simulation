import tkinter as tk
from tkinter import ttk
import random
import threading
import time

class BorderQueueSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Border Queue Visualizer with ETA")
        self.root.geometry("1200x800")
        
        # Simulation parameters
        self.max_queue_length = 50
        self.move_interval = 5  # seconds
        self.static_trucks_count = 3
        self.static_duration_periods = 4
        self.initial_trucks_to_pass = 0
        self.queue_length_threshold = 3
        
        # Queue state
        self.trucks = []
        self.running = False
        self.simulation_thread = None
        self.time_elapsed = 0
        self.trucks_crossed = 0
        
        self.setup_ui()
        self.initialize_queue()
        
    def setup_ui(self):
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Parameters input
        params_frame = ttk.LabelFrame(control_frame, text="Simulation Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=5)
        
        # Max queue length
        ttk.Label(params_frame, text="Maximum Queue Length:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.max_length_var = tk.StringVar(value=str(self.max_queue_length))
        ttk.Entry(params_frame, textvariable=self.max_length_var, width=10).grid(row=0, column=1, padx=5)
        
        # Move interval
        ttk.Label(params_frame, text="Move Interval (seconds):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.interval_var = tk.StringVar(value=str(self.move_interval))
        ttk.Entry(params_frame, textvariable=self.interval_var, width=10).grid(row=0, column=3, padx=5)
        
        # Static trucks count
        ttk.Label(params_frame, text="Static Trucks Count:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.static_count_var = tk.StringVar(value=str(self.static_trucks_count))
        ttk.Entry(params_frame, textvariable=self.static_count_var, width=10).grid(row=1, column=1, padx=5)
        
        # Static duration periods
        ttk.Label(params_frame, text="Static Duration (periods):").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.static_duration_var = tk.StringVar(value=str(self.static_duration_periods))
        ttk.Entry(params_frame, textvariable=self.static_duration_var, width=10).grid(row=1, column=3, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Start Simulation", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Simulation", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Queue", command=self.reset_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Apply Settings", command=self.apply_settings).pack(side=tk.LEFT, padx=5)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready to start simulation")
        ttk.Label(control_frame, textvariable=self.status_var).pack(pady=5)
        
        # Time and ETA display
        time_frame = ttk.LabelFrame(control_frame, text="Time & ETA Information", padding="10")
        time_frame.pack(fill=tk.X, pady=5)
        
        self.time_var = tk.StringVar(value="Time Elapsed: 0 seconds")
        ttk.Label(time_frame, textvariable=self.time_var).pack(side=tk.LEFT, padx=10)
        
        self.eta_var = tk.StringVar(value="Last Truck ETA: Calculating...")
        ttk.Label(time_frame, textvariable=self.eta_var).pack(side=tk.LEFT, padx=10)
        
        # Visualization area
        viz_frame = ttk.LabelFrame(self.root, text="Queue Visualization", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas for drawing the queue
        self.canvas = tk.Canvas(viz_frame, bg="white", height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Legend
        legend_frame = ttk.Frame(viz_frame)
        legend_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(legend_frame, text="Legend:").pack(side=tk.LEFT)
        
        # Create legend squares
        legend_canvas = tk.Canvas(legend_frame, height=50, width=800, bg="white")
        legend_canvas.pack(side=tk.LEFT, padx=10)
        
        legend_canvas.create_rectangle(10, 5, 30, 25, fill="blue", outline="black")
        legend_canvas.create_text(40, 15, text="Moving Truck", anchor=tk.W)
        
        legend_canvas.create_rectangle(120, 5, 140, 25, fill="red", outline="black")
        legend_canvas.create_text(150, 15, text="Static Truck (Can't Move)", anchor=tk.W)
        
        legend_canvas.create_rectangle(280, 5, 300, 25, fill="orange", outline="black")
        legend_canvas.create_text(310, 15, text="Just Became Movable", anchor=tk.W)
        
        legend_canvas.create_rectangle(450, 5, 470, 25, fill="lightgray", outline="black")
        legend_canvas.create_text(480, 15, text="Empty Position", anchor=tk.W)
        
        # Add explanation for periods
        legend_canvas.create_text(10, 35, text="'X periods left' = How many move cycles the red truck must wait before it can move again", 
                                anchor=tk.W, font=("Arial", 9), fill="darkred")
        
        # Statistics and details display
        stats_frame = ttk.LabelFrame(self.root, text="Queue Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_var = tk.StringVar()
        ttk.Label(stats_frame, textvariable=self.stats_var).pack()
        
        # Detailed truck info
        details_frame = ttk.LabelFrame(self.root, text="Truck Details", padding="10")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=scrollbar.set)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def initialize_queue(self):
        """Initialize the truck queue with position-dependent static durations"""
        self.trucks = []
        self.time_elapsed = 0
        self.trucks_crossed = 0
        
        for i in range(self.max_queue_length):
            truck = {
                'id': i + 1,
                'position': i,
                'is_static': False,
                'static_remaining': 0,
                'original_position': i,
                'wait_time': 0,
                'color': 'blue',
                'countdown_active': False
            }
            self.trucks.append(truck)
        
        # Randomly assign static trucks with position-dependent durations
        static_indices = random.sample(range(self.max_queue_length), 
                                     min(self.static_trucks_count, self.max_queue_length))
        
        # Define threshold for "near" vs "far" trucks
        position_threshold = self.max_queue_length // 2
        
        for idx in static_indices:
            self.trucks[idx]['is_static'] = True
            self.trucks[idx]['countdown_active'] = False
            self.trucks[idx]['color'] = 'red'
            # Shorter duration for trucks near border (lower positions)
            if idx <= position_threshold:
                self.trucks[idx]['static_remaining'] = random.randint(1, max(1, self.static_duration_periods // 1.5))
            # Longer duration for trucks far from border (higher positions)
            else:
                self.trucks[idx]['static_remaining'] = random.randint(1, self.static_duration_periods)
        
        # Calculate random number of trucks to pass before static countdown
        #min_trucks = max(1, self.max_queue_length // 10)
        #max_trucks = max(1, self.max_queue_length // 2)
        self.initial_trucks_to_pass = 4
    
    def apply_settings(self):
        """Apply user settings"""
        try:
            self.max_queue_length = int(self.max_length_var.get())
            self.move_interval = int(self.interval_var.get())
            self.static_trucks_count = int(self.static_count_var.get())
            self.static_duration_periods = int(self.static_duration_var.get())
            
            self.reset_queue()
            self.status_var.set("Settings applied successfully")
        except ValueError:
            self.status_var.set("Error: Please enter valid numbers")
    
    def reset_queue(self):
        """Reset the queue to initial state"""
        self.stop_simulation()
        self.initialize_queue()
        self.draw_queue()
        self.update_stats()
        self.update_details()
        self.status_var.set("Queue reset")
    
    def start_simulation(self):
        """Start the simulation"""
        if not self.running:
            self.running = True
            self.simulation_thread = threading.Thread(target=self.run_simulation)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            self.status_var.set("Simulation running...")
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1)
        self.status_var.set("Simulation stopped")
    
    def run_simulation(self):
        """Main simulation loop"""
        while self.running:
            # First update display, then wait, then update queue
            self.root.after(0, self.draw_queue)
            self.root.after(0, self.update_stats)
            self.root.after(0, self.update_details)
            self.root.after(0, self.calculate_eta)
            
            # Wait for the interval
            time.sleep(self.move_interval)
            
            # Then update the queue state
            self.time_elapsed += self.move_interval
            self.update_queue()
    
    def update_queue(self):
        """Update truck positions and states with improved movement logic"""
        if not self.trucks:
            return
        
        # Update wait times for all trucks
        for truck in self.trucks:
            truck['wait_time'] += self.move_interval
        
        # Sort trucks by position (front to back - position 0 is at border)
        self.trucks.sort(key=lambda x: x['position'])
        
        # Step 1: Check queue length for each static truck and decide if countdown should start
        # Step 1: Check queue length for each static truck and decide if countdown should start
        # Step 1: Check empty spots ahead for each static truck
        for truck in self.trucks:
            if truck['is_static'] and not truck['countdown_active']:
                current_pos = truck['position']
                
                # Count empty spaces ahead (positions in front of this truck)
                empty_ahead = 0
                for pos in range(current_pos - 1, -1, -1):  # from current-1 to 0
                    occupied = any(t['position'] == pos for t in self.trucks)
                    if not occupied:
                        empty_ahead += 1
                    else:
                        break  # stop counting once a truck is in front
                
                # Random threshold between 2 and 5
                required_spaces = random.randint(3, 6)
                
                if empty_ahead >= required_spaces:
                    truck['countdown_active'] = True

        
        # Step 2: Update static truck timers
        for truck in self.trucks:
            if truck['is_static'] and truck['countdown_active']:
                if truck['static_remaining'] > 0:
                    truck['static_remaining'] -= 1
                    truck['color'] = 'red'
                    if truck['static_remaining'] <= 0:
                        truck['is_static'] = False
                        truck['color'] = 'orange'
                        truck['countdown_active'] = False
        
        # Step 3: Find the first static truck with an active countdown
        first_active_static_position = None
        for truck in self.trucks:
            if truck['is_static'] and truck['countdown_active']:
                first_active_static_position = truck['position']
                break
        
        # Step 4: Process movement for all eligible trucks
        trucks_to_remove = []
        for i in range(len(self.trucks)):
            truck = self.trucks[i]
            
            # Skip if truck is behind a static truck with active countdown
            if first_active_static_position is not None and truck['position'] > first_active_static_position:
                continue
            
            # Handle trucks at the border (position 0)
            if truck['position'] == 0:
                if not truck['is_static'] or truck['countdown_active']:
                    trucks_to_remove.append(truck)
                    self.trucks_crossed += 1
                continue
            
            # Move non-static trucks to the nearest empty position
            if not truck['is_static']:
                current_position = truck['position']
                target_position = 0  # Default to border if no trucks ahead
                for pos in range(current_position - 1, -1, -1):
                    position_occupied = any(other_truck['position'] == pos 
                                          for other_truck in self.trucks if other_truck != truck)
                    if position_occupied:
                        target_position = pos + 1
                        break
                truck['position'] = target_position
        
        # Step 5: Remove trucks that crossed border
        for truck in trucks_to_remove:
            self.trucks.remove(truck)
        
        # Step 6: Update colors based on status
        for truck in self.trucks:
            if truck['is_static'] and truck['static_remaining'] > 0:
                truck['color'] = 'red'
            elif not truck['is_static'] and truck['color'] == 'red':
                truck['color'] = 'orange'
            elif truck['color'] == 'orange':
                truck['color'] = 'blue'
            elif not truck['is_static']:
                truck['color'] = 'blue'
    
    def calculate_eta(self):
        """Calculate ETA for the last truck"""
        if not self.trucks:
            self.eta_var.set("Last Truck ETA: All trucks crossed!")
            return
        
        # Find the truck at the back of the queue
        last_truck = max(self.trucks, key=lambda x: x['position'])
        
        # Calculate estimated time based on current queue dynamics
        total_trucks_ahead = last_truck['position']
        
        # Base time: number of trucks ahead × move interval
        base_time = total_trucks_ahead * self.move_interval
        
        # Add delay only for static trucks with active countdown
        static_delay = 0
        if self.trucks_crossed >= self.initial_trucks_to_pass:
            static_delay = sum(truck['static_remaining'] * self.move_interval 
                              for truck in self.trucks 
                              if truck['is_static'] and truck['countdown_active'])
        
        estimated_eta = base_time + static_delay
        
        self.eta_var.set(f"Last Truck ETA: ~{estimated_eta} seconds")
        self.time_var.set(f"Time Elapsed: {self.time_elapsed} seconds | Trucks Crossed: {self.trucks_crossed}")
    
    def draw_queue(self):
        """Draw the current queue state"""
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not yet initialized
            return
        
        # Calculate bar dimensions
        bar_width = max(20, (canvas_width - 40) // self.max_queue_length)
        bar_height = 40
        start_y = (canvas_height - bar_height) // 2
        
        # Draw background queue slots
        for i in range(self.max_queue_length):
            x = 20 + i * bar_width
            self.canvas.create_rectangle(x, start_y, x + bar_width - 2, start_y + bar_height,
                                       fill="lightgray", outline="black", width=1)
            self.canvas.create_text(x + bar_width//2, start_y + bar_height + 15,
                                  text=str(i), font=("Arial", 8))
        
        # Draw trucks in their current positions
        for truck in self.trucks:
            pos = truck['position']
            if 0 <= pos < self.max_queue_length:
                x = 20 + pos * bar_width
                self.canvas.create_rectangle(x, start_y, x + bar_width - 2, start_y + bar_height,
                                           fill=truck['color'], outline="black", width=2)
                
                # Add truck ID
                self.canvas.create_text(x + bar_width//2, start_y + bar_height//2,
                                      text=str(truck['id']), fill="white", font=("Arial", 10, "bold"))
                
                # Add static remaining time if applicable
                if truck['is_static'] and truck['static_remaining'] > 0:
                    # Show remaining periods above the truck
                    remaining_text = f"{truck['static_remaining']} periods left"
                    self.canvas.create_text(x + bar_width//2, start_y - 15,
                                          text=remaining_text, fill="red", font=("Arial", 8, "bold"))
                    
                    # Also show a small indicator
                    self.canvas.create_oval(x + bar_width - 8, start_y + 2, x + bar_width - 2, start_y + 8,
                                          fill="yellow", outline="red", width=2)
        
        # Draw border line
        border_x = 15
        self.canvas.create_line(border_x, start_y - 20, border_x, start_y + bar_height + 20,
                              fill="green", width=4)
        self.canvas.create_text(border_x, start_y - 30, text="BORDER", fill="green", font=("Arial", 12, "bold"))
        
        # Draw direction arrow (right to left movement)
        arrow_y = start_y - 50
        self.canvas.create_line(canvas_width - 50, arrow_y, 50, arrow_y, fill="blue", width=2, arrow=tk.LAST)
        self.canvas.create_text(canvas_width//2, arrow_y - 15, text="Direction of Movement (Right → Left)", fill="blue", font=("Arial", 10))
    
    def update_stats(self):
        """Update statistics display"""
        if not self.trucks:
            self.stats_var.set("All trucks have crossed the border!")
            return
        
        total_trucks = len(self.trucks)
        static_trucks = sum(1 for truck in self.trucks if truck['is_static'])
        moving_trucks = total_trucks - static_trucks
        
        # Calculate average wait time
        avg_wait_time = sum(truck['wait_time'] for truck in self.trucks) / total_trucks if total_trucks > 0 else 0
        
        stats_text = (f"Trucks in Queue: {total_trucks} | Moving: {moving_trucks} | "
                     f"Static: {static_trucks} | Avg Wait Time: {avg_wait_time:.1f}s | "
                     f"Trucks Crossed: {self.trucks_crossed}")
        self.stats_var.set(stats_text)
    
    def update_details(self):
        """Update detailed truck information"""
        self.details_text.delete(1.0, tk.END)
        
        if not self.trucks:
            self.details_text.insert(tk.END, "No trucks remaining in queue.\n")
            return
        
        # Sort trucks by position for display
        sorted_trucks = sorted(self.trucks, key=lambda x: x['position'])
        
        details = "Truck Details (Position | ID | Status | Wait Time | Static Remaining):\n"
        for truck in sorted_trucks:
            if truck['is_static']:
                status = f"STATIC({truck['static_remaining']}p)"
                static_info = f"{truck['static_remaining']}p"
            else:
                status = "MOVING"
                static_info = "N/A"
            details += (f"Pos {truck['position']:2d} | ID {truck['id']:2d} | {status:10s} | "
                       f"{truck['wait_time']:3d}s | {static_info}\n")
        
        self.details_text.insert(tk.END, details)

def main():
    root = tk.Tk()
    app = BorderQueueSimulator(root)
    
    # Bind window close event
    def on_closing():
        app.stop_simulation()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

def main():
    root = tk.Tk()
    app = BorderQueueSimulator(root)
    
    # Bind window close event
    def on_closing():
        app.stop_simulation()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

