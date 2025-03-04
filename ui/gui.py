from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from core.logic import is_valid, bfs_solution, get_possible_moves

# Menu screen
class MainMenuFrame(tk.Frame):
    def __init__(self, master, start_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="skyblue")
        title = tk.Label(self, text="Sang sông", font=("Arial", 36), bg="skyblue")
        title.pack(pady=50)
        start_button = ctk.CTkButton(self, text="Bắt đầu", font=("Arial", 24), corner_radius=20, command=lambda: (print("Bắt đầu game"), start_callback()))
        start_button.pack(pady=20)

# Game Screen
class GameFrame(tk.Frame):
    def __init__(self, master, end_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.end_callback = end_callback
        self.config(bg="skyblue")
        self.canvas_width = 600

        self.canvas_height = 700
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="skyblue")
        self.canvas.pack(side="top", fill="both", expand=True)

        # 2 bờ sông
        self.left_bank = 0
        self.left_bank_right = 200
        self.right_bank_left = 600
        self.right_bank = 800

        self.boat_positions = {
            0: (self.left_bank_right - 10, 450),   # (190, 450)
            1: (self.right_bank_left + 10, 450)      # (610, 450)
        }
        self.positions = {
            'W': {0: (100, 350), 1: (700, 350)},
            'G': {0: (100, 250), 1: (700, 250)},
            'C': {0: (100, 150), 1: (700, 150)}
        }

        self.boat_img = ImageTk.PhotoImage(Image.open("img/boat.png").resize((150, 75), Image.Resampling.LANCZOS))
        self.wolf_img = ImageTk.PhotoImage(Image.open("img/wolf.webp").resize((60, 60), Image.Resampling.LANCZOS))
        self.goat_img = ImageTk.PhotoImage(Image.open("img/goat.webp").resize((60, 60), Image.Resampling.LANCZOS))
        self.cabbage_img = ImageTk.PhotoImage(Image.open("img/cabbage.webp").resize((60, 60), Image.Resampling.LANCZOS))
        self.boatman_icon = ImageTk.PhotoImage(Image.open("img/boatman.webp").resize((50, 50), Image.Resampling.LANCZOS))
        self.assist_icon = ImageTk.PhotoImage(Image.open("img/help.png").resize((50, 50), Image.Resampling.LANCZOS))
        self.auto_icon = ImageTk.PhotoImage(Image.open("img/machine.png").resize((50, 50), Image.Resampling.LANCZOS))
        self.reset_icon = ImageTk.PhotoImage(Image.open("img/restart.png").resize((50, 50), Image.Resampling.LANCZOS))
 
        self.state = 0  
        self.selected = []  # Các obj được chọn (W, G, C)
        self.selected_offsets = {}

        control_frame = tk.Frame(self, bg="skyblue")
        control_frame.pack(side="bottom", pady=10)

        # move btn
        btn_frame_move = tk.Frame(control_frame, bg="skyblue")
        btn_frame_move.pack(side="left", padx=10)
        self.move_button = ctk.CTkButton(btn_frame_move, text="", image=self.boatman_icon, command=self.user_move,
                                        corner_radius=20, fg_color="gray", hover_color="#333333", width=40, height=40)
        self.move_button.pack()
        move_label = tk.Label(btn_frame_move, text="Đi", font=("Arial", 14), bg="skyblue")
        move_label.pack()

        # auto play btn
        btn_frame_auto = tk.Frame(control_frame, bg="skyblue")
        btn_frame_auto.pack(side="left", padx=10)
        self.auto_button = ctk.CTkButton(btn_frame_auto, text="", image=self.auto_icon, command=self.auto_play,
                                        corner_radius=20, fg_color="gray", hover_color="#333333", width=40, height=40)
        self.auto_button.pack()
        auto_label = tk.Label(btn_frame_auto, text="Máy chơi", font=("Arial", 14), bg="skyblue")
        auto_label.pack()

        # restart btn
        btn_frame_reset = tk.Frame(control_frame, bg="skyblue")
        btn_frame_reset.pack(side="left", padx=10)
        self.reset_button = ctk.CTkButton(btn_frame_reset, text="", image=self.reset_icon, command=self.reset_game,
                                        corner_radius=20, fg_color="gray", hover_color="#333333", width=40, height=40)
        self.reset_button.pack()
        reset_label = tk.Label(btn_frame_reset, text="Chơi lại", font=("Arial", 14), bg="skyblue")
        reset_label.pack()

        # assist btn
        btn_frame_assist = tk.Frame(control_frame, bg="skyblue")
        btn_frame_assist.pack(side="left", padx=10)
        self.assist_button = ctk.CTkButton(btn_frame_assist, text="", image=self.assist_icon, command=self.assist,
                                        corner_radius=20, fg_color="gray", hover_color="#333333", width=40, height=40)
        self.assist_button.pack()
        assist_label = tk.Label(btn_frame_assist, text="Trợ giúp", font=("Arial", 14), bg="skyblue")
        assist_label.pack()

        self.message_label = tk.Label(control_frame, text="Trạng thái: 0000", font=("Arial", 14), bg="skyblue")
        self.message_label.pack(side="left", padx=10)

        # Bắt click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.entity_items = {}  # Lưu obj id: {'W': id, 'G': id, 'C': id}
        self.boat_items = []    # Lưu boat id

        self.draw_background()
        self.draw_items()
       
    def draw_background(self):
        self.canvas.delete("background")
        self.canvas.create_rectangle(self.left_bank, 0, self.left_bank_right, self.canvas_height, fill="lightgreen", outline="", tags="background")
        self.canvas.create_rectangle(self.left_bank_right, 0, self.right_bank_left, self.canvas_height, fill="deepskyblue", outline="", tags="background")
        self.canvas.create_rectangle(self.right_bank_left, 0, self.right_bank, self.canvas_height, fill="lightgreen", outline="", tags="background")

    def draw_items(self):
        self.canvas.delete("entity")
        self.entity_items = {}
        self.boat_items = []
       # boat+manboat
        boat_man_bank = self.get_boat_man_bank()
        boat_pos = self.boat_positions[boat_man_bank]
        boat_item = self.canvas.create_image(boat_pos[0], boat_pos[1], image=self.boat_img, tags="entity")
        self.boat_items = [boat_item]
        # wolf, goat, cabbage
        for entity in ['W', 'G', 'C']:
            bank = self.get_entity_bank(entity)
            pos = self.positions[entity][bank]
            if entity == 'W':
                img = self.wolf_img
            elif entity == 'G':
                img = self.goat_img
            elif entity == 'C':
                img = self.cabbage_img
            item = self.canvas.create_image(pos[0], pos[1], image=img, tags="entity")
            self.entity_items[entity] = item
        self.message_label.config(text="Trạng thái: {:04b}".format(self.state))

    def get_boat_man_bank(self):
        return (self.state >> 0) & 1

    def get_entity_bank(self, entity):
        if entity == 'W':
            return (self.state >> 1) & 1
        elif entity == 'G':
            return (self.state >> 2) & 1
        elif entity == 'C':
            return (self.state >> 3) & 1

    def animate_move(self, items, target_center, steps=20, delay=50, callback=None):
        if not items:
            if callback: callback()
            return
        coords = self.canvas.coords(items[0])
        current_center = (coords[0], coords[1])
        dx = (target_center[0] - current_center[0]) / steps
        dy = (target_center[1] - current_center[1]) / steps
        def step(count):
            if count < steps:
                for item in items:
                    self.canvas.move(item, dx, dy)
                self.after(delay, lambda: step(count+1))
            else:
                if callback: callback()
        step(0)

    def update_positions(self):
        boat_man_bank = self.get_boat_man_bank()
        boat_center = self.boat_positions[boat_man_bank]
        self.animate_move(self.boat_items, boat_center)
        for entity in ['W', 'G', 'C']:
            if entity in self.selected:
                offset = self.selected_offsets.get(entity, (0, 0))
                target = (boat_center[0] + offset[0], boat_center[1] + offset[1])
                self.animate_move([self.entity_items[entity]], target)
            else:
                bank = self.get_entity_bank(entity)
                target = self.positions[entity][bank]
                self.animate_move([self.entity_items[entity]], target)
        self.message_label.config(text="Trạng thái: {:04b}".format(self.state))

    def get_boat_target(self, entity):
        boat_center = self.boat_positions[self.get_boat_man_bank()]
        offset = self.selected_offsets.get(entity, (0, 0))
        return (boat_center[0] + offset[0], boat_center[1] + offset[1])

    def on_canvas_click(self, event):
        for entity in ['W', 'G', 'C']:
            current_pos = self.canvas.coords(self.entity_items[entity])
            # Kiểm tra nếu click nằm trong vùng có r =  20 (20^2 = 400) từ pos hiện tại
            if (event.x - current_pos[0])**2 + (event.y - current_pos[1])**2 <= 400:
                # Nếu obj chưa được chọn => chỉ cho phép nếu obj đang ở cùng bờ với thuyền
                if entity not in self.selected:
                    if self.get_entity_bank(entity) != self.get_boat_man_bank():
                        # Nếu obj không nằm trên cùng bờ với thuyền => pass
                        break
                    if len(self.selected) < 2:
                        self.selected.append(entity)
                        offset = (-30, 0) if len(self.selected) == 1 else (30, 0)
                        self.selected_offsets[entity] = offset
                        boat_center = self.boat_positions[self.get_boat_man_bank()]
                        target = (boat_center[0] + offset[0], boat_center[1] + offset[1])
                        self.animate_move([self.entity_items[entity]], target, steps=10, delay=30)
                    else:
                        self.message_label.config(text="Chỉ được chọn tối đa 2 khách!")
                else:
                    self.selected.remove(entity)
                    if entity in self.selected_offsets:
                        del self.selected_offsets[entity]
                    bank = self.get_entity_bank(entity)
                    bank_target = self.positions[entity][bank]
                    self.animate_move([self.entity_items[entity]], bank_target, steps=10, delay=30)
                break


    def user_move(self):
        new_state = self.state
        new_state ^= 1  # Đảo bit của thuyền
        for entity in self.selected:
            if entity == 'W':
                new_state ^= (1 << 1)
            elif entity == 'G':
                new_state ^= (1 << 2)
            elif entity == 'C':
                new_state ^= (1 << 3)
        if is_valid(new_state):
            self.state = new_state
            self.selected = []
            self.selected_offsets = {}
            self.update_positions()
            if self.state == 15:
                self.after(1100, lambda: self.end_callback("victory"))
        else:
            boat_man_bank = (new_state >> 0) & 1
            wolf_bank = (new_state >> 1) & 1
            goat_bank = (new_state >> 2) & 1
            cabbage_bank = (new_state >> 3) & 1
            if wolf_bank == goat_bank and boat_man_bank != wolf_bank and cabbage_bank != wolf_bank:
                failure_entity = 'W'
            elif goat_bank == cabbage_bank and boat_man_bank != goat_bank and wolf_bank != goat_bank:
                failure_entity = 'G'
            else:
                failure_entity = None
            self.state = new_state
            self.update_positions()
            if failure_entity:
                self.after(1100, lambda: self.animate_failure(failure_entity))
            else:
                self.after(1100, lambda: self.end_callback("defeat"))
            self.selected = []
            self.selected_offsets = {}
            
    # animation for fail cases:
    def animate_failure(self, failure_entity):
        if failure_entity == 'W':
            bank = self.get_entity_bank('W')
            target = self.positions['G'][bank]
            item = self.entity_items.get('W')
            self.canvas.lift(item)
        elif failure_entity == 'G':
            bank = self.get_entity_bank('G')
            target = self.positions['C'][bank]
            item = self.entity_items.get('G')
            self.canvas.lift(item)
        else:
            item = None
        if item:
            self.animate_move([item], target, callback=lambda: self.end_callback("defeat"))
        else:
            self.after(1100, lambda: self.end_callback("defeat"))


    def reset_game(self):
        self.state = 0
        self.selected = []
        self.selected_offsets = {}
        self.draw_items()

    def auto_play(self):
        solution = bfs_solution(self.state)
        if solution is None:
            messagebox.showinfo("Thông báo", "Bạn không thể hoàn thành nhiệm vụ")
            return
        self.auto_moves = solution
        self.play_next_move(0)

    def play_next_move(self, index):
        if index < len(self.auto_moves):
            state, moved = self.auto_moves[index]
            self.state = state
            self.draw_items()
            self.after(1100, lambda: self.play_next_move(index+1))
        else:
            messagebox.showinfo("Chúc mừng", "Máy đã hoàn thành nhiệm vụ!")

    def assist(self):
        solution = bfs_solution(self.state)
        if solution is None:
            messagebox.showinfo("Thông báo", "Bạn không thể hoàn thành nhiệm vụ")
        else:
            if len(solution) > 1:
                next_state, moved = solution[1]
                next_bank = ((next_state >> 0) & 1) + 1
                move_text = "Thuyền chuyển qua bờ {} ".format(next_bank)
                if moved:
                    move_text += "cùng " + ", ".join(moved)
                else:
                    move_text += "mà không mang theo khách nào"
                messagebox.showinfo("Hướng dẫn", move_text)
            else:
                messagebox.showinfo("Thông báo", "Đã tới đích")

# End game screen
class ResultFrame(tk.Frame):
    def __init__(self, master, result, restart_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="skyblue")
        result_text = "Victory" if result=="victory" else "Defeat"
        result_label = tk.Label(self, text=result_text, font=("Arial", 36), bg="skyblue")
        result_label.pack(pady=50)
        restart_button = ctk.CTkButton(self, text="Chơi lại", font=("Arial", 24), command=restart_callback, corner_radius=20)
        restart_button.pack(pady=20)
        exit_button = ctk.CTkButton(self, text="Thoát", font=("Arial", 24), command=master.quit, corner_radius=20)
        exit_button.pack(pady=20)

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sang sông")
        self.geometry("800x800")
        self.resizable(False, False)
        self.current_frame = None
        self.show_main_menu()
    
    def show_frame(self, frame_class, *args, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args, **kwargs)
        self.current_frame.pack(fill="both", expand=True)
    
    def show_main_menu(self):
        self.show_frame(MainMenuFrame, start_callback=self.start_game)
    
    def start_game(self):
        print("start_game() called")
        self.show_frame(GameFrame, end_callback=self.end_game)  


    def end_game(self, result):
        self.show_frame(ResultFrame, result=result, restart_callback=self.start_game)

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()
