import googleapiclient.discovery
def credentials_to_dict(credentials):
	return {'token': credentials.token,
	'refresh_token': credentials.refresh_token,
	'token_uri': credentials.token_uri,
	'client_id': credentials.client_id,
	'client_secret': credentials.client_secret,
	'scopes': credentials.scopes}

def get_user_info(credentials):
	"""Send a request to the UserInfo API to retrieve the user's information.

	Args:
	credentials: oauth2client.client.OAuth2Credentials instance to authorize the
	request.
	Returns:
	User information as a dict.
	"""
	user_info_service = googleapiclient.discovery.build("oauth2", "v2", credentials=credentials)
	user_info = user_info_service.userinfo().get().execute()
	return user_info

def reply_detect(thread_id,email,credentials):
	gmail_service = googleapiclient.discovery.build("gmail", "v1", credentials=credentials)
	messages_list = gmail_service.users().threads().get(id=thread_id, userId=email).execute()

	# iterate for RE subject
	for message in messages_list["messages"]:
		for header in message["payload"]["headers"]:
			if header["name"].lower() == "subject" and "Re:" in header["value"]:
				return True
	return False