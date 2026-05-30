import cv2
import tkinter as tk
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk
import os

FONT_TYPE = "meiryo"

class App(customtkinter.CTk):
    def __init__(self):

        super().__init__()

        #メンバー変数の設定
        self.fonts = (FONT_TYPE,15)
        self.movie = None
        self.total_frames = 0
        self.fps = 30
        self.current_frame_number = 0
        self.is_playing = False
        self.is_reverse = False  # 逆再生中かどうかのフラグ
        
                
        #画像の保持
        self.tk_img = None
        
        #キャンパスサイズ
        self.canvas_w = 800
        self.canvas_h = 450
        
        #フォームのセットアップをする
        self.setup_form()

    def setup_form(self):
        # --- UIレイアウト ---
        
        #動画ファイル読み込みフレームの設定
        self.read_file_frame = ReadFileFrame(master=self,header_name = "動画ファイル読み込み")
        self.read_file_frame.grid(row=0,column=0,padx=20,pady=20,sticky="ew")


        # 基準のframeの画像を表示するキャンパス.
        self.frame_canvas = customtkinter.CTkCanvas(self, width=self.canvas_w, height=self.canvas_h, bg="#DCE4EE", highlightthickness=0)
        self.frame_canvas.grid(row=1, column=0,padx=20, pady=10, sticky="nsew")

        self.info_label =  customtkinter.CTkLabel(self, text="Frame: 0 / 0 | Time: 0.00s / 0.00s",font = self.fonts)
        self.info_label.grid(row=2, column=0,padx=20, pady=10, sticky="nsew")

        #動画から読み取った画像を表示するフレームの設定
        self.button_frame = ButtonFrame(master=self,header_name = "ボタン")
        self.button_frame.grid(row=3,column=0,padx=20,pady=20,sticky="ew")
        
        self.scale_var = tk.DoubleVar()
        self.scale = customtkinter.CTkSlider(
            master=self,
            from_=0,
            to=100,             # 動画読み込み時に後で更新されます
            variable=self.scale_var,
            command=self.on_slider_move,
            # デザイン調整（お好みで変えてください）
            height=15,          # 全体の高さ
            button_length=5,   # つまみの大きさ
            width = 600
        )
        self.scale.grid(row=4,column=0,padx=5,pady=(0,5))
        

        # キーボードショートカット
        self.bind("<Left>", lambda e: self.button_frame.prev_frame())
        self.bind("<Right>", lambda e: self.button_frame.next_frame())
        self.bind("c", lambda e: self.copy_time_to_clipboard())


        self.update_loop()
        
    # --- メインループ ---
    def update_loop(self):
        if self.is_playing:
            self.button_frame.next_frame()
        elif self.is_reverse:
            self.button_frame.prev_frame()
        
        # 待機時間
        wait_time = int(1000/self.fps)
        self.after(wait_time, self.update_loop)
        

    def copy_time_to_clipboard(self):
        curr_sec = self.current_frame_number / self.fps
        time_str = f"{curr_sec}"
        self.clipboard_clear()
        self.clipboard_append(time_str)
        #print(f"Copied to clipboard: {time_str}")
        
        
    def render_frame(self):
        if self.movie and self.movie.isOpened():
            self.movie.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number)
            ret, frame = self.movie.read()
            if ret:
                self.display_image(frame)
                
    def next_render_frame(self):
        if self.movie and self.movie.isOpened():
            ret, frame = self.movie.read()
            if ret:
                self.display_image(frame)
            else:
                # 動画の終端に達した場合の処理
                self.is_playing = False
                self.button_frame.play_button.configure(text="再生(Space)")

    # render_frame と next_render_frame の共通処理を切り出し
    def display_image(self, frame):
        h, w = frame.shape[:2]
        if h > w:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            h, w = frame.shape[:2]
        
        aspect = w / h
        if aspect > (self.canvas_w / self.canvas_h):
            new_w = self.canvas_w
            new_h = int(new_w / aspect)
        else:
            new_h = self.canvas_h
            new_w = int(new_h * aspect)
        
        frame = cv2.resize(frame, (new_w, new_h))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.tk_img = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.frame_canvas.delete("all")
        self.frame_canvas.create_image(self.canvas_w//2, self.canvas_h//2, anchor="center", image=self.tk_img)
        
        curr_sec = self.current_frame_number / self.fps
        total_sec = self.total_frames / self.fps
        self.info_label.configure(
            text=f"Frame: {self.current_frame_number} / {self.total_frames - 1} | "
                 f"Time: {curr_sec:.3f}s / {total_sec:.3f}s (FPS: {self.fps:.2f})"
        )
        self.scale_var.set(self.current_frame_number)
        
    def on_slider_move(self, event):
        self.current_frame_number = int(float(event))
        self.render_frame()


class ReadFileFrame(customtkinter.CTkFrame):
    
    def __init__(self,master,header_name="ReadFileFrame", **kwargs):
        super().__init__(master=master,**kwargs)
        self.app = master
        
        #メンバ関数の設定
        self.fonts = (FONT_TYPE,15)
        self.header_name = header_name
        
        #フォームのセットアップをする
        self.setup_form()
        
    def setup_form(self):
        #レイアウト設定
        self.grid_rowconfigure(0,weight=1) #行方向
        self.grid_columnconfigure(0,weight=1) #列方向
        
        #動画ファイルパスを指定するテキストボックス
        self.movie_textbox = customtkinter.CTkEntry(master=self,placeholder_text="動画ファイルを読み込む",width=120,font=self.fonts)
        self.movie_textbox.grid(row=0,column=0,padx=10,pady=(0,10),sticky="ew")
        
        #動画ファイル選択ボタン
        self.movie_select = customtkinter.CTkButton(master=self,fg_color="transparent",border_width=2,text_color=("gray10","#DCE4EE"),
                                                     command=lambda:self.movie_select_callback(self.movie_textbox),text="ファイル選択",font=self.fonts)
        self.movie_select.grid(row=0,column=1,padx=10,pady=(0,10))
        
        #ロードボタン
        self.button_load = customtkinter.CTkButton(master=self,command=self.button_load_callback,text="読み込む",font=self.fonts)
        self.button_load.grid(row=0,column=2,padx=10,pady=(0,10))
        
    def movie_select_callback(self,textbox):
        """
        選択ボタンが押されたときのコールバック。ファイル選択ダイアログを表示する
        """
        #エクスプローラーを表示してファイルを選択する
        file_name = ReadFileFrame.movie_file_read()
        
        if file_name is not None:
            #ファイルパスをテキストボックスに記入
            textbox.delete(0,tk.END)
            textbox.insert(0,file_name)
            
            
    def button_load_callback(self):
        """
        開くボタンが押されたときのコールバック。
        """
        movie_file_path = self.movie_textbox.get()
        self.app.current_frame_number = 0
        self.app.movie = cv2.VideoCapture(movie_file_path)
        
        if self.app.movie.isOpened():
            self.app.total_frames = int(self.app.movie.get(cv2.CAP_PROP_FRAME_COUNT))
            self.app.fps = self.app.movie.get(cv2.CAP_PROP_FPS)
            self.app.current_frame_number = 0
            self.app.scale.configure(to=self.app.total_frames - 1)
            self.app.render_frame()
        
            
            
    @staticmethod
    def movie_file_read():
        """
        ファイル選択ダイアログを表示する
        """

        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = tk.filedialog.askopenfilename(filetypes=[("動画ファイル","*.mov *.mp4")],initialdir=current_dir)
        
        if len(file_path) != 0:
            return file_path
        else:
            return None
        
        
class ButtonFrame(customtkinter.CTkFrame):
    
    def __init__(self,master,header_name="ReadFileFrame", **kwargs):
        super().__init__(master=master,**kwargs)
        self.app = master
        
        #メンバ関数の設定
        self.fonts = (FONT_TYPE,8)
        self.header_name = header_name
        
        self.button_w = 60
        self.button_h = 20
        
        #フォームのセットアップをする
        self.setup_form()
        
    def setup_form(self):
        #レイアウト設定
        self.grid_rowconfigure(0,weight=1) #行方向
        self.grid_columnconfigure(0,weight=1) #列方向
    

        # 戻る系ボタン
        self.go_back_one_second_button = customtkinter.CTkButton(master= self, width=self.button_w,height=self.button_h, text="<< 1秒", command=self.skip_backward,font=self.fonts)
        self.go_back_half_second_button = customtkinter.CTkButton(master= self, width=self.button_w,height=self.button_h, text="<< 0.5秒", command=self.skip_half_backward,font=self.fonts)
        self.go_back_frame_button = customtkinter.CTkButton(master= self, width=self.button_w,height=self.button_h, text="◀1frame", command=self.prev_frame,font=self.fonts)
        
        self.go_back_one_second_button.grid(row=0,column=0,padx=5,pady=(0,5))
        self.go_back_half_second_button.grid(row=0,column=1,padx=5,pady=(0,5))
        self.go_back_frame_button.grid(row=0,column=2,padx=5,pady=(0,5))
        
        
        # 逆再生ボタン
        self.reverse_play_button = customtkinter.CTkButton(master = self, width=self.button_w,height=self.button_h,text="逆再生", command=self.toggle_reverse,font = self.fonts)
        self.reverse_play_button.grid(row=0,column=3,padx=5,pady=(0,5))
        
        # 再生ボタン
        self.play_button = customtkinter.CTkButton(master = self, width=self.button_w,height=self.button_h, text="再生(Space)", command=self.toggle_play,font = self.fonts)
        self.play_button.grid(row=0,column=4,padx=5,pady=(0,5))
        
        # 進む系ボタン
        self.go_next_frame_button = customtkinter.CTkButton(master=self, width=self.button_w,height=self.button_h, text="1frame▶", command=self.next_frame,font =self.fonts)
        self.go_half_second_button = customtkinter.CTkButton(master=self, width=self.button_w,height=self.button_h, text="0.5秒 >>", command=self.skip_half_forward,font =self.fonts)
        self.go_one_second_button = customtkinter.CTkButton(master=self, width=self.button_w,height=self.button_h, text="1秒 >>", command=self.skip_forward,font =self.fonts)
        
        self.go_next_frame_button.grid(row=0,column=5,padx=5,pady=(0,5))
        self.go_half_second_button.grid(row=0,column=6,padx=5,pady=(0,5))
        self.go_one_second_button.grid(row=0,column=7,padx=5,pady=(0,5))

        
        # --- 逆再生制御 ---
    def toggle_reverse(self):
        """逆再生の状態を切り替える"""
        self.app.is_reverse = not self.app.is_reverse
        if self.app.is_reverse:
            self.app.is_playing = False # 通常再生は止める
            self.reverse_play_button.configure(text="一時停止")
            self.play_button.configure(text = "再生")
        else:
            self.reverse_play_button.configure(text="逆再生")

    def toggle_play(self):
        """通常再生の状態を切り替える"""
        self.app.is_playing = not self.app.is_playing
        if self.app.is_playing:
            self.app.is_reverse = False # 逆再生は止める
            self.play_button.configure(text="一時停止")
            self.reverse_play_button.configure(text="逆再生")
        else:
            self.play_button.configure(text="再生")

    # --- フレーム移動 ---
    def next_frame(self):
        if self.app.current_frame_number < self.app.total_frames - 1:
            self.app.current_frame_number += 1
            self.app.next_render_frame()
            
        else:
            self.app.is_playing = False
            self.play_button.configure(text="再生")

    def prev_frame(self):
        if self.app.current_frame_number > 0:
            self.app.current_frame_number -= 1
            self.app.render_frame()
        else:
            self.app.is_reverse = False
            self.reverse_play_button.configure(text="逆再生(J)")

    # (その他の load_video, render_frame, rotate_video 等は変更なし)
    def skip_forward(self):
        skip_amount = int(self.app.fps)
        self.app.current_frame_number = min(self.app.total_frames - 1, self.app.current_frame_number + skip_amount)
        self.app.render_frame()

    def skip_backward(self):
        skip_amount = int(self.app.fps)
        self.app.current_frame_number = max(0, self.app.current_frame_number - skip_amount)
        self.app.render_frame()

    def skip_half_forward(self):
        skip_amount = int(self.app.fps/2)
        self.app.current_frame_number = min(self.app.total_frames - 1, self.app.current_frame_number + skip_amount)
        self.app.render_frame()

    def skip_half_backward(self):
        skip_amount = int(self.app.fps/2)
        self.app.current_frame_number = max(0, self.app.current_frame_number - skip_amount)
        self.app.render_frame()


if __name__ == "__main__":
    app = App()
    app.mainloop()