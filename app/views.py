from app import app, db, my_tz, CLIENT_SECRETS_FILE, SCOPES
import celery
import json
import flask
from datetime import datetime, timedelta
from flask import jsonify,request
from email.mime.text import MIMEText
import base64
from models import User,Campaign
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from auth_helper import *

@app.route('/schedule_campaign',methods=['POST'])
def schedule_mailer():
	keys = ["recipients","camp_title","templates","wait_days","stages","email","temp_vars"]
	params = {}
	for key in keys:
		if key not in request.get_json():
			return jsonify({"status":"Error","message":"parameter " + key + " missing"})
	params = request.get_json()
	if params["stages"] != len(params["templates"]):
		return jsonify({"status":"Error","message":"Number of templates should be equal to number of stages"})
	if len(params["temp_vars"]) != len(params["templates"]):
		return jsonify({"status":"Error","message":"Number of templates should be equal to list of template parameters"})
	print ", ".join(params["recipients"])

	for i in range(params["stages"]):
		eta = my_tz.localize(datetime.now()) + timedelta(days=i*params["wait_days"])
		# eta = my_tz.localize(datetime.now()) + timedelta(seconds=i*params["wait_days"])
		send_async_email.apply_async(args=[params["camp_title"],",".join(params["recipients"]),params["templates"][i],params["temp_vars"][i],params["email"]],eta=eta)
	return jsonify({"status":"Success","message":"Mails Scheduled"})

@celery.task
def send_async_email(camp_title,recipients,template,temp_var,email):
	with app.app_context():
		user = User.query.filter_by(user_id=email).all()
		credentials = dict(json.loads(user[0].credentials))
		credentials = google.oauth2.credentials.Credentials(**credentials)
		user[0].credentials = json.dumps(credentials_to_dict(credentials))
		db.session.commit()
		for key in temp_var:
			if key in template:
				template = template.replace(key,temp_var[key])
		gmail_service = googleapiclient.discovery.build("gmail", "v1", credentials=credentials)
		message = MIMEText(template)
		message['to'] = recipients
		message['from'] = email
		message['subject'] = camp_title
		body = {'raw': base64.b64encode(message.as_string())}
		try:
			camp_obj = Campaign.query.filter_by(camp_title=camp_title).all()
			#if reply of previous followup detected .. send no further mails
			if camp_obj and camp_obj[0].thread_id and reply_detect(camp_obj[0].thread_id,email,credentials):
				print "Reply detected."
				return
			message = gmail_service.users().messages().send(userId=email, body=body).execute()
			thread_id = message["threadId"]
			# if campaign does not exist.. create one
			if not camp_obj:
				new_camp_obj = Campaign(camp_title,thread_id)
				db.session.add(new_camp_obj)
				db.session.commit()
			# else update to thread id of last mail to current one.
			else:
				camp_obj[0].thread_id = thread_id
				db.session.commit()

		except Exception as error:
			print "Error occured" + str(error)


@app.route('/authorize')
def authorize():
	email = request.args.get("email")
	user = User.query.filter_by(user_id=email).all()
	if user:
		return jsonify({"status":"Error","message":"User already authorized"})
	# Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
	CLIENT_SECRETS_FILE, scopes=SCOPES)

	flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

	authorization_url, state = flow.authorization_url(
	# Enable offline access so that you can refresh an access token without
	# re-prompting the user for permission. Recommended for web server apps.
	access_type='offline',approval_prompt="force")

	# Store the state so the callback can verify the auth server response.
	flask.session['state'] = state

	return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  	if "state" not in flask.session:
		return jsonify({"status":"Error","message":"Not allowed"})
	state = flask.session['state']

	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
	flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	authorization_response = flask.request.url
	flow.fetch_token(authorization_response=authorization_response)

	credentials = flow.credentials
	user_info = get_user_info(credentials)
	email= user_info.get('email')
	user = User.query.filter_by(user_id=email).all()
	if user:
		return jsonify({"status":"Error","message":"User already authorized"})
	user = User(email,json.dumps(credentials_to_dict(credentials)))
	db.session.add(user)
	db.session.commit()

	return jsonify({"status":"Success","message":"credentials stored in db"})
	