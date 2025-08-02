"""
Image Handling API Routes
Handles image retrieval and serving from different directories
"""
from flask import Blueprint, jsonify, request, send_file
from pathlib import Path
from urllib.parse import unquote
from .utils.file_parser import get_image_file_path_by_filename

# Create image handling blueprint
image_bp = Blueprint('image', __name__)


@image_bp.route('/afm-files/image/<path:filename>/<path:decoded_point_number>', methods=['GET'])
def get_profile_image(filename, decoded_point_number):
    """Get profile image from tiff_dir for a specific measurement point"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename and point number
        decoded_filename = unquote(filename)
        decoded_point_number = unquote(decoded_point_number)
        
        # Extract site information from query parameters
        site_info = {
            'site_id': request.args.get('site_id'),     # Keep as string
            'site_x': request.args.get('site_x'),       # Keep as string
            'site_y': request.args.get('site_y'),       # Keep as string
            'point_no': request.args.get('point_no')    # Will convert to int
        }
        
        # Only convert point_no to integer (for 4-digit formatting)
        if site_info['point_no']:
            try:
                site_info['point_no'] = int(site_info['point_no'])
            except ValueError:
                site_info['point_no'] = None
        
        print(f"\n=== IMAGE API REQUEST ===")
        print(f"Tool: {tool_name}")
        print(f"Filename (encoded): '{filename}'")
        print(f"Filename (decoded): '{decoded_filename}'")
        print(f"Site ID (encoded): '{decoded_point_number}'")
        print(f"Site ID (decoded): '{decoded_point_number}'")
        print(f"Complete site info: {site_info}")
        
        # Find matching image file using the utility function
        image_path = get_image_file_path_by_filename(decoded_filename, decoded_point_number, tool_name, site_info)
        
        if not image_path:
            return jsonify({
                'success': False,
                'error': 'Image file not found',
                'message': f'No image file found for filename: {decoded_filename}, point: {decoded_point_number} in tool {tool_name}',
                'tool': tool_name
            }), 404
        
        # Check if file exists
        if not image_path.exists():
            return jsonify({
                'success': False,
                'error': 'Image file not accessible',
                'message': f'Image file {image_path.name} exists in listing but not accessible',
                'tool': tool_name
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'filename': image_path.name,
                'path': str(image_path),
                'relative_path': f'tiff_dir/{image_path.name}',
                'url': f'/api/afm-files/image-file/{decoded_filename}/{decoded_point_number}?tool={tool_name}'
            },
            'tool': tool_name,
            'message': f'Successfully found image for {decoded_filename}, point {decoded_point_number} from {tool_name}'
        })
        
    except Exception as e:
        print(f"Error in get_profile_image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to find image for {decoded_filename}, point {decoded_point_number}'
        }), 500


@image_bp.route('/afm-files/image-file/<path:filename>/<path:point_number>', methods=['GET'])
def serve_profile_image(filename, point_number):
    """Serve the actual image file (legacy endpoint)"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename and point number
        decoded_filename = unquote(filename)
        decoded_point_number = unquote(point_number)
        
        # Extract site information from query parameters
        site_info = {
            'site_id': request.args.get('site_id'),     # Keep as string
            'site_x': request.args.get('site_x'),       # Keep as string
            'site_y': request.args.get('site_y'),       # Keep as string
            'point_no': request.args.get('point_no')    # Will convert to int
        }
        
        # Only convert point_no to integer (for 4-digit formatting)
        if site_info['point_no']:
            try:
                site_info['point_no'] = int(site_info['point_no'])
            except ValueError:
                site_info['point_no'] = None
        
        print(f"\n=== IMAGE FILE SERVE REQUEST ===")
        print(f"Tool: {tool_name}")
        print(f"Filename (encoded): '{filename}'")
        print(f"Filename (decoded): '{decoded_filename}'")
        print(f"Site ID (encoded): '{point_number}'")
        print(f"Site ID (decoded): '{decoded_point_number}'")
        print(f"Complete site info: {site_info}")
        
        # Find matching image file using the utility function
        image_path = get_image_file_path_by_filename(decoded_filename, decoded_point_number, tool_name, site_info)
        
        if not image_path or not image_path.exists():
            return "Image file not found", 404
        
        return send_file(image_path, mimetype='image/webp')
        
    except Exception as e:
        print(f"Error serving image: {e}")
        return f"Error serving image: {str(e)}", 500


@image_bp.route('/afm-files/images/<image_type>', methods=['GET'])
def get_images_by_type(image_type):
    """Get list of images from specific directory type (profile, tiff, align, tip)"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        filename = request.args.get('filename')
        point_id = request.args.get('point_id', 'default')
        
        # URL decode the filename
        decoded_filename = unquote(filename) if filename else None
        
        print(f"\n=== IMAGES LIST API REQUEST ===")
        print(f"Tool: {tool_name}")
        print(f"Image Type: {image_type}")
        print(f"Filename: '{decoded_filename}'")
        print(f"Point ID: '{point_id}'")
        
        # Define base directory for the tool
        base_dir = Path(f"itc-afm-data-platform-pjt-shared/AFM_DB/{tool_name}")
        
        # Map image types to directory names
        dir_mapping = {
            'profile': 'profile_dir',
            'tiff': 'tiff_dir',
            'align': 'align_dir',
            'tip': 'tip_dir'
        }
        
        if image_type not in dir_mapping:
            return jsonify({
                'success': False,
                'error': 'Invalid image type',
                'message': f'Image type must be one of: {list(dir_mapping.keys())}'
            }), 400
        
        # Get the directory path
        image_dir = base_dir / dir_mapping[image_type]
        
        if not image_dir.exists():
            return jsonify({
                'success': True,
                'data': {
                    'images': [],
                    'directory': str(image_dir),
                    'type': image_type
                },
                'message': f'Directory not found: {image_dir}'
            })
        
        # List all image files in the directory
        # For now, we'll return all images, but you can filter by filename pattern if needed
        image_extensions = ['.webp', '.png', '.jpg', '.jpeg', '.tiff', '.tif']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(image_dir.glob(f'*{ext}'))
        
        # Filter by filename if provided
        if decoded_filename:
            # Extract base filename pattern from the AFM filename
            # Remove the hash marks and extension
            base_pattern = decoded_filename.replace('#', '').split('.')[0]
            filtered_files = []
            
            for img_file in image_files:
                if base_pattern in img_file.name or decoded_filename in img_file.name:
                    filtered_files.append(img_file)
            
            image_files = filtered_files
        
        # Convert to relative paths and names
        images_data = []
        for img_file in sorted(image_files):
            images_data.append({
                'name': img_file.name,
                'size': img_file.stat().st_size,
                'modified': img_file.stat().st_mtime
            })
        
        print(f"Found {len(images_data)} images in {image_type} directory")
        
        return jsonify({
            'success': True,
            'data': {
                'images': images_data,
                'directory': str(image_dir),
                'type': image_type,
                'count': len(images_data)
            },
            'message': f'Successfully retrieved {len(images_data)} images from {image_type} directory'
        })
        
    except Exception as e:
        print(f"Error in get_images_by_type: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to retrieve images for type: {image_type}'
        }), 500


@image_bp.route('/afm-files/image-file/<path:filename>/<path:point_id>/<image_type>/<image_name>', methods=['GET'])
def serve_image_by_type(filename, point_id, image_type, image_name):
    """Serve image file from specific directory type"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        
        # URL decode parameters
        decoded_filename = unquote(filename)
        decoded_point_id = unquote(point_id)
        decoded_image_name = unquote(image_name)
        
        print(f"\n=== SERVE IMAGE BY TYPE REQUEST ===")
        print(f"Tool: {tool_name}")
        print(f"Filename: '{decoded_filename}'")
        print(f"Point ID: '{decoded_point_id}'")
        print(f"Image Type: {image_type}")
        print(f"Image Name: '{decoded_image_name}'")
        
        # Define base directory for the tool
        base_dir = Path(f"itc-afm-data-platform-pjt-shared/AFM_DB/{tool_name}")
        
        # Map image types to directory names
        dir_mapping = {
            'profile': 'profile_dir',
            'tiff': 'tiff_dir',
            'align': 'align_dir',
            'tip': 'tip_dir'
        }
        
        if image_type not in dir_mapping:
            return "Invalid image type", 400
        
        # Get the image path
        image_path = base_dir / dir_mapping[image_type] / decoded_image_name
        
        if not image_path.exists():
            print(f"Image not found at: {image_path}")
            return "Image file not found", 404
        
        # Determine mimetype based on extension
        ext = image_path.suffix.lower()
        mimetype_mapping = {
            '.webp': 'image/webp',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        
        mimetype = mimetype_mapping.get(ext, 'application/octet-stream')
        
        return send_file(image_path, mimetype=mimetype)
        
    except Exception as e:
        print(f"Error serving image by type: {e}")
        return f"Error serving image: {str(e)}", 500