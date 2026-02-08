import plotly.graph_objects as go
import os
import sys # sysモジュールを追加して、エラーメッセージをより明確にする

# my_opp3.py と同じディレクトリに画像があることを前提
current_dir = os.path.dirname(os.path.abspath(__file__))
image_filename = "1692743634004.jpg"
image_path = os.path.join(current_dir, image_filename)

# --- デバッグ情報の出力 ---
print(f"--- デバッグ情報 ---")
print(f"現在のスクリプトのディレクトリ: {current_dir}")
print(f"画像ファイル名: {image_filename}")
print(f"画像ファイルの絶対パス: {image_path}")

if not os.path.exists(image_path):
    print(f"エラー: 指定された画像ファイルが見つかりません。パスを確認してください。")
    print(f"期待されるパス: {image_path}")
    sys.exit(1) # スクリプトを終了
else:
    print(f"画像ファイルは存在します: {image_path}")
    # ファイルサイズも確認してみる
    print(f"ファイルサイズ: {os.path.getsize(image_path)} バイト")

print(f"--- Plotly描画開始 ---")

# 画像の実際のサイズ (前回確認した 600x360 ピクセル)
image_width = 600
image_height = 360

fig = go.Figure()

fig.add_layout_image(
    dict(
        source=image_path,
        xref="x",
        yref="y",
        x=0,
        y=0,
        sizex=image_width,
        sizey=image_height,
        sizing="fill",
        layer="below",
        opacity=1.0
    )
)

fig.update_layout(
    xaxis=dict(range=[0, image_width], showgrid=False, zeroline=False, visible=False),
    yaxis=dict(range=[image_height, 0], showgrid=False, zeroline=False, visible=False),
    height=image_height,
    width=image_width,
    margin=dict(l=0, r=0, t=0, b=0)
)

fig.show() # このコマンドを実行するとブラウザでPlotlyの図が表示されます

print(f"--- Plotly描画終了。ブラウザを確認してください。---")