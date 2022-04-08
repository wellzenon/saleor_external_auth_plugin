CONFIGURATION_FIELD = "providers_config_list"
DEFAULT_CONFIGURATION_TEXT = """---
# Configuration in YAML format
# A dict with providers identified by name and 
# each provider itself has the foolowing fields:
# name (again), client_id, client_secret, redirect_uri, 
# auth_uri, tokens_uri and user_info_uri
#
# the last 3 uri (auth_uri, tokens_uri and user_info_uri) are dicts
# with path and extra_params fields that the uri:
#
# https://auth.com?scope=email profile&access_type=offline
# 
# would come from 
#
# auth_uri: 
#         path: "https://auth.com"
#         extra_params:
#             scope: "email profile"
#             access_type: "offline"
#
google: 
    name: "google"
    client_id: "your google id"
    client_secret: "your google secret"
    redirect_uri: "http://localhost:3000/auth/google"
    auth_uri: 
        path: "https://accounts.google.com/o/oauth2/v2/auth"
        extra_params:
            scope: "openid email profile"
            access_type: "offline"
            include_granted_scopes: "true"
            response_type: "code"
    tokens_uri:
        path: "https://oauth2.googleapis.com/token"
        extra_params: 
            grant_type: "authorization_code"
    user_info_uri: 
        path: "https://www.googleapis.com/oauth2/v2/userinfo"
facebook:
    name: "facebook"
    client_id: "your facebook id"
    client_secret: "your facebook secret"
    redirect_uri: "http://localhost:3000/auth/facebook"
    auth_uri: 
        path: "https://www.facebook.com/v13.0/dialog/oauth"
        extra_params:
    tokens_uri:
        path: "https://graph.facebook.com/v13.0/oauth/access_token"
        extra_params: 
            grant_type: "authorization_code"
    user_info_uri: 
        path: "https://graph.facebook.com/v13.0/me"
        extra_params:
            fields: "id,name,email,first_name,last_name,middle_name,is_guest_user,picture{url,height,width}"
"""
