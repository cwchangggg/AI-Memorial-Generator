from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse, JsonResponse
import os
from .utils import run_pipeline_models
from django.contrib.auth.decorators import login_required
from .models import MemorialPage, GeneratedVideo,FlowerOffering

FLOWER_MAP = {
    '🌸': '櫻花',
    '🌼': '雛菊',
    '🌹': '玫瑰',
    '🌻': '向日葵',
    '💐': '花束',
}

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
                yield "data: 影片完成\n\n"
            else:
                yield "data: 影片生成失敗\n\n"

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

    return render(request, 'upload.html')



@login_required
def create_memorial(request):
    videos = GeneratedVideo.objects.filter(user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        biography = request.POST.get('biography')
        video_id = request.POST.get('memorial_video')
        cover = request.FILES.get('cover_photo')

        selected_video = GeneratedVideo.objects.get(id=video_id) if video_id else None

        page = MemorialPage.objects.create(
            owner=request.user,
            title=title,
            biography=biography,
            cover_photo=cover,
            memorial_video=selected_video
        )

        return redirect(f'/memorial/{page.id}/')

    return render(request, 'create_memorial.html', {'videos': videos})

def memorial_detail(request, memorial_id):
    page = get_object_or_404(MemorialPage, id=memorial_id)
    is_owner = request.user == page.owner
    flowers = page.flowers.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        flower_type = request.POST.get('flower_type')
        message = request.POST.get('message')

        if name and flower_type:
            FlowerOffering.objects.create(
                memorial_page=page,
                name=name,
                flower_type=flower_type,
                message=message
            )
            return redirect(f'/memorial/{memorial_id}/')

    return render(request, 'memorial_detail.html', {
        'page': page,
        'flowers': flowers,
        'emoji': '🌼'
    })

