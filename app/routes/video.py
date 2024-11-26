# This file is deprecated and has been split into modular components.
# The code has been moved to:
#   - app/routes/video/__init__.py
#   - app/routes/video/process.py
#   - app/routes/video/search.py
#
# Please use the new modular structure instead.

from app.routes.video import init_video_routes

# Re-export the init_video_routes function for backward compatibility
__all__ = ['init_video_routes']