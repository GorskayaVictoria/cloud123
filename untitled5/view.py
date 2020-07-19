import mimetypes
import os
import uuid
from wsgiref.util import FileWrapper

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from django.views.static import serve

from untitled5.settings import AZURE_STORAGE_CONNECTION_STRING, BASE_DIR

from untitled5.forms import UploadForm


def index(request):
    return render(
        request, 'index.html',
        context={})


def upload(request):
    if request.method == "POST":
        form = UploadForm(request.POST,request.FILES)
        if form.is_valid():
            profile_pic = form.cleaned_data["profile_pic"]
            if profile_pic != "":
                file_name = 'quickstart' + str(uuid.uuid4()) + '.'+str(profile_pic.content_type).split("/")[1]
                blob_s_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
                blob_client = blob_s_client.get_blob_client(container='images', blob=file_name)
                blob_client.upload_blob(profile_pic)
            # return redirect(reverse("index"))
            return redirect(download_file,pk=file_name)
        else:
            return render(request, "upload.html", {"form": form})
    else:
        return render(request, "upload.html", {"form": UploadForm()})


def download_file(request,pk):
    return render(request, "download.html", {"pk": pk})



def download(request,pk):
    print(pk)
    download_path = os.path.join(BASE_DIR, pk)
    blob_s_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_s_client.get_blob_client(container='images', blob=pk)
    with open(download_path,"wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(pk, 'rb'), chunk_size),
                                    content_type=mimetypes.guess_type(pk)[0])
    response['Content-Length'] = os.path.getsize(pk)
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(pk)
    return response