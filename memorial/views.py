from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse, JsonResponse
import os
from .utils import run_pipeline_models
from django.contrib.auth.decorators import login_required
from .models import GeneratedVideo

UPLOAD_DIR = 'media/'

@login_required
def my_videos(request):
    videos = GeneratedVideo.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_videos.html', {'videos': videos})


@login_required(login_url='/login/')
@csrf_exempt
def upload_and_generate(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        audio_file = request.FILES.get('audio')

        if not text or not audio_file:
            return JsonResponse({'error': '請輸入文字與聲音檔案'}, status=400)

        audio_path = os.path.join(UPLOAD_DIR, audio_file.name)
        video_path = os.path.join(UPLOAD_DIR, 'output.mp4')

        with open(audio_path, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        def event_stream():
            yield "data: 正在啟動模型...\n\n"
            for output in run_pipeline_models(text, audio_path, video_path):
                yield f"data: {output}\n\n"

            if os.path.exists(video_path):
                # save to database
                GeneratedVideo.objects.create(
                    user=request.user,
                    text=text,
                    audio_filename=audio_file.name,
                    video_path=video_path,
                )
                yield "data: 完成\n\n"
            else:
                yield "data: 影片生成失敗\n\n"

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

    return render(request, 'upload.html')
