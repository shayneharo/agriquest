"""
Authentication API endpoints for React frontend integration
"""

from flask import Blueprint, jsonify, session

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

@auth_api_bp.route('/status')
def get_auth_status():
    """Get current authentication status"""
    try:
        if 'user_id' in session:
            user_data = {
                'id': session['user_id'],
                'username': session.get('username'),
                'role': session.get('role'),
                'authenticated': True
            }
            
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': user_data
            })
        else:
            return jsonify({
                'success': True,
                'authenticated': False,
                'user': None
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Successfully logged out'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
