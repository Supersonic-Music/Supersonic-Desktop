video_player = "mpv"
audio_player = "mplayer"
_3d_Viewer = "f3d"
image_viewer = "gwenview"
text_viewer = "kate"
python_exec = "python"

mimetypes_list = {
    "mp3": audio_player,
    "m4a": audio_player,
    "ogg": audio_player,
    "wma": audio_player,
    "oga": audio_player,
    "mogg": audio_player,
    "opus": audio_player,

    "wmv": video_player,
    "mp4": video_player,
    "webm": video_player,
    "mkv": video_player,

    "obj": _3d_Viewer,
    "stl": _3d_Viewer,
    "fbx": _3d_Viewer,
    "gltf": _3d_Viewer,
    "glb": _3d_Viewer,
    "usd": _3d_Viewer,

    "txt": text_viewer,

    "py": python_exec,

    "json": text_viewer,

    "png": image_viewer,
    "jpg": image_viewer,
    "jpeg": image_viewer,
}
