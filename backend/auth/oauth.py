from authlib.integrations.starlette_client import OAuth
from fastapi import Request, HTTPException
import os

# OAuth Configuration
oauth = OAuth()

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_meta_data_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

async def get_google_user_info(request: Request, token: dict):
    """Get user info from Google OAuth"""
    try:
        client = oauth.google
        resp = await client.get('userinfo', token=token)
        user_info = resp.json()
        return {
            'google_id': user_info.get('sub'),
            'email': user_info.get('email'),
            'full_name': user_info.get('name'),
            'avatar_url': user_info.get('picture'),
            'email_verified': user_info.get('email_verified', False)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {str(e)}")

async def get_github_user_info(request: Request, token: dict):
    """Get user info from GitHub OAuth"""
    try:
        client = oauth.github
        
        # Get user profile
        resp = await client.get('user', token=token)
        user_info = resp.json()
        
        # Get user emails
        email_resp = await client.get('user/emails', token=token)
        emails = email_resp.json()
        
        # Find primary email
        primary_email = None
        for email in emails:
            if email.get('primary'):
                primary_email = email.get('email')
                break
        
        return {
            'github_id': str(user_info.get('id')),
            'email': primary_email or user_info.get('email'),
            'username': user_info.get('login'),
            'full_name': user_info.get('name'),
            'avatar_url': user_info.get('avatar_url'),
            'bio': user_info.get('bio'),
            'company': user_info.get('company'),
            'location': user_info.get('location'),
            'website': user_info.get('blog'),
            'email_verified': True  # GitHub emails are verified
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth error: {str(e)}")