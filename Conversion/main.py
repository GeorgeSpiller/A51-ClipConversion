import os
from tkinter import Y
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from skimage.filters import gaussian
import datetime
from multiprocessing import cpu_count

YOUTUBE_SHORT_DIMENTIONS = (1080, 1080)
YOUTUBE_4K_DIMENTIONS = (2560, 1440)
RENAME_PREFIX_SHORTS = ""
RENAME_PREFIX_STREAM = "[Stream] "
RENAME_PREFIX_INSTA = "[Insta] "

BLUR_AMOUNT = 8


def blur(image):
    """ Returns a blurred version of the image """
    return gaussian(image.astype(float), sigma=BLUR_AMOUNT)


def get_clips_in_dir(dir_footage_child):
    L = []
    for root, dirs, files in os.walk(dir_footage_child):
        for file in files:
            if os.path.splitext(file)[1] == '.mp4':
                filePath = os.path.join(root, file)
                # video = file_to_VideoFileClip(filePath)
                L.append(filePath)
    return L


def isShort(mediaLength):
    if mediaLength > 60:
        return False
    return True


def add_shorts_vfx(VClip, doCenterClipZoom=True):

    CZP = 1.6   # Center Zoom Percentage
    VClip = VClip.resize(width=1080) # (1080x607)

    # center clip 
    if doCenterClipZoom:
        VClipCenter = VClip.resize(newsize=CZP)
        VClipCenter = VClipCenter.set_position(("center","center")).margin(top=640, bottom=640)
        # center clip banners
        VClipCenterTop = VClip.crop(x1=0, y1=0, x2=1080, y2=90).set_position((0, 640-90))
        # bottom banner:
        # VClipCenterBottom = VClip.crop(x1=0, y1=440, x2=1080, y2=607).set_position((0, 1300))

        # blur clips
        VClipBlur = VClip.fl_image( blur ).resize(height=640)
        VClipBottom = VClipBlur.crop(x1=0, y1=90, x2=1080, y2=640).set_position((0, 1400))

        final = CompositeVideoClip(clips=[VClipCenter, VClipBlur, VClipBottom, VClipCenterTop], size=(1080, 1920))
    else:
        VClipCenter = VClip.set_position(("center","center")).margin(top=640, bottom=640, color=(1, 0, 0))

        # blur clips
        VClipBlur = VClip.fl_image( blur ).resize(height=640)# 640
        VClipBottom = VClipBlur.set_position((0, 1280))

        final = CompositeVideoClip(clips=[VClipCenter, VClipBlur, VClipBottom], size=(1080, 1920))
    
    return final


def resize_media(dir_input, shortsFlag=True, streamsFlag=True, centerZoom=True):
    #TODO: mark the already convertied clips in some way
    #TODO: Change short aspect ratio and include a blur for the top black bars
    mediaPathList = get_clips_in_dir(dir_input)
    
    for mediaPath in mediaPathList:
        currMedia = VideoFileClip(mediaPath)
        if isShort(currMedia.duration):
            if shortsFlag:
                currMediaShortsName = RENAME_PREFIX_SHORTS + mediaPath.split(dir_input)[1].replace('\\', '').replace('.mp4', ' #shorts.mp4')
                # currMediaInstaName = RENAME_PREFIX_INSTA + mediaPath.split(dir_input)[1].replace('\\', '')

                ShortsMedia = add_shorts_vfx(currMedia, doCenterClipZoom=centerZoom)
                ShortsMedia.write_videofile(filename=f'Output\\{currMediaShortsName}', codec='libx264', audio=True)

                # instaMedia = currMedia.fx( vfx.resize, (1080, 1080) )
                # instaMedia.write_videofile(filename=f'Output\\{currMediaInstaName}', codec='libx264', audio=True)
        else:
            if streamsFlag:
                currMediaName = RENAME_PREFIX_STREAM + mediaPath.split(dir_input)[1].replace('\\', '')
                currMedia = currMedia.fx( vfx.resize, YOUTUBE_4K_DIMENTIONS )
                currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True)




def speedTest_upscale():
    mediaPathList = get_clips_in_dir(dir_input)
    
    for mediaPath in mediaPathList:
        currMedia = VideoFileClip(mediaPath)
        if isShort(currMedia.duration):
            continue

        currMediaName = RENAME_PREFIX_STREAMUPSCALE + mediaPath.split(dir_input)[1].replace('\\', '')
        currMedia = currMedia.subclip(0, 3)
        currMedia = currMedia.fx( vfx.resize, YOUTUBE_4K_DIMENTIONS )

        #start_time = datetime.datetime.now()
        #end_time = datetime.datetime.now()
        #print(end_time - start_time)

        print('\n--- basic ---\n')
        currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True)

        print('\n--- multithreading ---\n')
        currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True, threads=cpu_count())


        try:
            print('\n--- cuda unspecified device ---\n')
            currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True, threads=cpu_count(),
                                  ffmpeg_params=['-hwaccel', 'cuda'])
        except Exception:
            print('failed.')


        try:
            print('\n--- cuda device 0---\n')
            currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True, threads=cpu_count(),
                                  ffmpeg_params=['-hwaccel_device', 0, '-hwaccel', 'cuda'])
        except Exception:
            print('failed.')

    
        try:
            print('\n--- opencl ---\n')
            currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True, threads=cpu_count(),
                                  ffmpeg_params=['-x264opts', 'opencl'])
        except Exception:
            print('failed.')
    

        try:
            print('\n--- opencl as param ---\n')
            currMedia.write_videofile(filename=f'Output\\{currMediaName}', codec='libx264', audio=True, threads=cpu_count(),
                                  ffmpeg_params=['-x264-params', 'opencl=true'])
        except Exception:
            print('failed.')
            

if __name__ == "__main__":
    dir_input_noZoom = os.path.join(os.path.dirname(__file__), 'Input-NoZoom')
    resize_media(dir_input_noZoom, streamsFlag=False, centerZoom=False)

    dir_input_Zoom = os.path.join(os.path.dirname(__file__), 'Input-WithZoom')
    resize_media(dir_input_Zoom, streamsFlag=False, centerZoom=True)

