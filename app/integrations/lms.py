import requests
from datetime import datetime
from flask import current_app
import logging
from app.models import LMSIntegration
from app import db

logger = logging.getLogger(__name__)

class LMSConnector:
    """Base class for LMS integrations"""
    def __init__(self, platform, user_id):
        self.platform = platform
        self.user_id = user_id
        self.integration = LMSIntegration.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()
        
    def is_configured(self):
        """Check if LMS integration is configured"""
        return bool(self.integration and self.integration.access_token)
    
    def needs_refresh(self):
        """Check if token needs refresh"""
        if not self.integration:
            return True
        return (self.integration.token_expiry and 
                self.integration.token_expiry <= datetime.utcnow())
    
    def update_tokens(self, access_token, refresh_token, expiry):
        """Update integration tokens"""
        if not self.integration:
            self.integration = LMSIntegration(
                user_id=self.user_id,
                platform=self.platform
            )
            db.session.add(self.integration)
        
        self.integration.access_token = access_token
        self.integration.refresh_token = refresh_token
        self.integration.token_expiry = expiry
        self.integration.last_sync = datetime.utcnow()
        db.session.commit()

class MoodleConnector(LMSConnector):
    """Moodle-specific LMS connector"""
    def __init__(self, user_id):
        super().__init__('moodle', user_id)
        self.base_url = current_app.config['LMS_BASE_URL']
        
    def authenticate(self, username, password):
        """Authenticate with Moodle"""
        try:
            response = requests.post(
                f"{self.base_url}/login/token.php",
                data={
                    'username': username,
                    'password': password,
                    'service': 'moodle_mobile_app'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'token' in data:
                self.update_tokens(
                    access_token=data['token'],
                    refresh_token=None,  # Moodle doesn't use refresh tokens
                    expiry=None  # Tokens don't expire in Moodle
                )
                return True
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Moodle authentication error: {str(e)}")
            return False
    
    def get_courses(self):
        """Get user's enrolled courses"""
        if not self.is_configured():
            return []
            
        try:
            response = requests.get(
                f"{self.base_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.integration.access_token,
                    'wsfunction': 'core_enrol_get_users_courses',
                    'userid': self.user_id,
                    'moodlewsrestformat': 'json'
                }
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Moodle courses: {str(e)}")
            return []
    
    def get_assignments(self, course_id=None):
        """Get assignments for all courses or specific course"""
        if not self.is_configured():
            return []
            
        try:
            params = {
                'wstoken': self.integration.access_token,
                'wsfunction': 'mod_assign_get_assignments',
                'moodlewsrestformat': 'json'
            }
            if course_id:
                params['courseids[]'] = course_id
                
            response = requests.get(
                f"{self.base_url}/webservice/rest/server.php",
                params=params
            )
            response.raise_for_status()
            return response.json().get('courses', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Moodle assignments: {str(e)}")
            return []

class BlackboardConnector(LMSConnector):
    """Blackboard-specific LMS connector"""
    def __init__(self, user_id):
        super().__init__('blackboard', user_id)
        self.base_url = current_app.config['LMS_BASE_URL']
        self.client_id = current_app.config['BLACKBOARD_CLIENT_ID']
        self.client_secret = current_app.config['BLACKBOARD_CLIENT_SECRET']
        
    def authenticate(self, username, password):
        """Authenticate with Blackboard"""
        try:
            # Get OAuth2 token
            response = requests.post(
                f"{self.base_url}/learn/api/public/v1/oauth2/token",
                data={
                    'grant_type': 'password',
                    'username': username,
                    'password': password
                },
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            data = response.json()
            
            if 'access_token' in data:
                self.update_tokens(
                    access_token=data['access_token'],
                    refresh_token=data.get('refresh_token'),
                    expiry=datetime.utcnow().timestamp() + data['expires_in']
                )
                return True
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Blackboard authentication error: {str(e)}")
            return False
    
    def refresh_token(self):
        """Refresh Blackboard access token"""
        if not self.integration or not self.integration.refresh_token:
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/learn/api/public/v1/oauth2/token",
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.integration.refresh_token
                },
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            data = response.json()
            
            self.update_tokens(
                access_token=data['access_token'],
                refresh_token=data.get('refresh_token'),
                expiry=datetime.utcnow().timestamp() + data['expires_in']
            )
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing Blackboard token: {str(e)}")
            return False
    
    def get_courses(self):
        """Get user's enrolled courses"""
        if not self.is_configured():
            return []
            
        if self.needs_refresh() and not self.refresh_token():
            return []
            
        try:
            response = requests.get(
                f"{self.base_url}/learn/api/public/v1/users/{self.user_id}/courses",
                headers={'Authorization': f"Bearer {self.integration.access_token}"}
            )
            response.raise_for_status()
            return response.json().get('results', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Blackboard courses: {str(e)}")
            return []
    
    def get_assignments(self, course_id=None):
        """Get assignments for all courses or specific course"""
        if not self.is_configured():
            return []
            
        if self.needs_refresh() and not self.refresh_token():
            return []
            
        try:
            assignments = []
            if course_id:
                courses = [course_id]
            else:
                courses = [c['id'] for c in self.get_courses()]
                
            for cid in courses:
                response = requests.get(
                    f"{self.base_url}/learn/api/public/v1/courses/{cid}/gradebook/columns",
                    headers={'Authorization': f"Bearer {self.integration.access_token}"}
                )
                response.raise_for_status()
                assignments.extend(response.json().get('results', []))
                
            return assignments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Blackboard assignments: {str(e)}")
            return []

def get_lms_connector(platform, user_id):
    """Factory function to get appropriate LMS connector"""
    connectors = {
        'moodle': MoodleConnector,
        'blackboard': BlackboardConnector
    }
    
    connector_class = connectors.get(platform.lower())
    if not connector_class:
        raise ValueError(f"Unsupported LMS platform: {platform}")
        
    return connector_class(user_id) 