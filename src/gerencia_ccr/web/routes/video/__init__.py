from flask import Blueprint
from .process import init_process_routes
from .search import init_search_routes

video_bp = Blueprint('video', __name__)

def init_video_routes(services_collection):
    init_process_routes(video_bp, services_collection)
    init_search_routes(video_bp, services_collection)
    return video_bp