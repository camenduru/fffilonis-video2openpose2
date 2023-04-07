import gradio as gr
from controlnet_aux import OpenposeDetector
import os
import cv2
import numpy as np
from PIL import Image
from moviepy.editor import *

openpose = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

def get_frames(video_in):
    frames = []
    #resize the video
    clip = VideoFileClip(video_in)
    
    #check fps
    if clip.fps > 30:
        print("vide rate is over 30, resetting to 30")
        clip_resized = clip.resize(height=512)
        clip_resized.write_videofile("video_resized.mp4", fps=30)
    else:
        print("video rate is OK")
        clip_resized = clip.resize(height=512)
        clip_resized.write_videofile("video_resized.mp4", fps=clip.fps)
    
    print("video resized to 512 height")
    
    # Opens the Video file with CV2
    cap= cv2.VideoCapture("video_resized.mp4")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("video fps: " + str(fps))
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        cv2.imwrite('kang'+str(i)+'.jpg',frame)
        frames.append('kang'+str(i)+'.jpg')
        i+=1
    
    cap.release()
    cv2.destroyAllWindows()
    print("broke the video into frames")
    
    return frames, fps

def get_openpose_filter(i):
    image = Image.open(i)
    
    #image = np.array(image)

    image = openpose(image)
    #image = Image.fromarray(image)
    image.save("openpose_frame_" + str(i) + ".jpeg")
    return "openpose_frame_" + str(i) + ".jpeg"

def create_video(frames, fps, type):
    print("building video result")
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(type + "_result.mp4", fps=fps)
    
    return type + "_result.mp4"

def convertG2V(imported_gif):
    clip = VideoFileClip(imported_gif.name)
    clip.write_videofile("my_gif_video.mp4")
    return "my_gif_video.mp4"
    
def infer(video_in):
    
    
    # 1. break video into frames and get FPS
    break_vid = get_frames(video_in)
    frames_list= break_vid[0]
    fps = break_vid[1]
    #n_frame = int(trim_value*fps)
    n_frame = len(frames_list)
    
    if n_frame >= len(frames_list):
        print("video is shorter than the cut value")
        n_frame = len(frames_list)
    
    # 2. prepare frames result arrays
    result_frames = []
    print("set stop frames to: " + str(n_frame))
    
    for i in frames_list[0:int(n_frame)]:
        openpose_frame = get_openpose_filter(i)
        result_frames.append(openpose_frame)
        print("frame " + i + "/" + str(n_frame) + ": done;")

    
    final_vid = create_video(result_frames, fps, "openpose")

    files = [final_vid]

    return final_vid, files

title="""
<div style="text-align: center; max-width: 500px; margin: 0 auto;">
        <div
        style="
            display: inline-flex;
            align-items: center;
            gap: 0.8rem;
            font-size: 1.75rem;
            margin-bottom: 10px;
        "
        >
        <h1 style="font-weight: 600; margin-bottom: 7px;">
            Video to OpenPose
        </h1>
        </div>
       
    </div>
"""

with gr.Blocks() as demo:
    with gr.Column():
        gr.HTML(title)
        with gr.Row():
            with gr.Column():
                video_input = gr.Video(source="upload", type="filepath")
                gif_input = gr.File(label="import a GIF instead", file_types=['.gif'])
                gif_input.change(fn=convertG2V, inputs=gif_input, outputs=video_input)
                submit_btn = gr.Button("Submit")
            
            with gr.Column():
                video_output = gr.Video()
                file_output = gr.Files()

    submit_btn.click(fn=infer, inputs=[video_input], outputs=[video_output, file_output])

demo.launch()