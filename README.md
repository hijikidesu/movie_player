# movie_player
1フレーム単位で映像を飛ばすことができる自作動画再生プレイヤーです

# 作成経緯
SOUND VOLTEXのプレイ映像を1フレーム単位で確認したかったので作成しました。

# 使い方
1."Download ZIP"や "git clone"でコードをダウンロード

2.`movie_check.py`を実行

3.「ファイル選択」ボタンから再生したい動画ファイルを選択し、「読み込む」ボタンを押す

4.ctrl+cで現在表示している秒数をコピーできる

<img width="913" height="832" alt="Image" src="https://github.com/user-attachments/assets/4c13852c-f7f0-4d7f-93c4-3471e5ccef4f" />

# 動作確認環境
・conda 24.11.3

・python 3.14.3

・opencv 4.12.0 

・pillow 12.0.0

・tk 8.6.15 

・customtkinter 5.2.2 

# 注意点
・映像確認を目的として作成したため、音声は再生されません

・一般的なメディアプレイヤーのようにヌルヌル再生はされません

・逆再生は再生より速度が遅いです
