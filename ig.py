#!/usr/bin/python

from instagram.client import InstagramAPI
import pytumblr
from datetime import datetime
import os
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("creds.ini")

def get_tumblr_client():
  # Authenticate via OAuth
  #if tumblr_client: return tumblr_client
  tumblr_client = pytumblr.TumblrRestClient(
     config.get("tumblr", "consumer_key"),
     config.get("tumblr", "consumer_secret"),
     config.get("tumblr", "token"),
     config.get("tumblr", "token_secret")
  )
  return tumblr_client

def get_last_post_date(tag=None):
  client = get_tumblr_client()
  # Make the request
  #print client.blog_info('tedder42.tumblr.com')
  postdata = client.posts('tedder42.tumblr.com', tag=tag, limit=1, reblog_info=True)
  posts = postdata.get('posts', {})
  if len(posts) > 0:
    post_date = datetime.utcfromtimestamp(posts[0].get('timestamp'))
    #print post_date
    return post_date
  return None

def get_ig_client():
  #if ig_client: return ig_client
  ig_client = InstagramAPI(
    access_token=config.get("instagram", "access_token"),
    client_id=config.get("instagram", "client_id"),
    client_secret=config.get("instagram", "client_secret")
  )
  return ig_client

def get_ig_media():
  api = get_ig_client()
  medialist = api.user_recent_media(1451272066)
  return medialist[0]

def process_feed():
  client = get_tumblr_client()
  medialist = get_ig_media()
  post_date = get_last_post_date(tag='instagram')
  #print post_date
  if not post_date:
    print "we should have a post_date, it's weird there is none. bailing."
    return None

  for media in reversed(medialist):
    #print dir(media)
    #print media.images.get('standard_resolution').url
    caption = ''
    if media.caption:
      caption = media.caption.text
    #print post_date
    #print media.created_time
    if (not post_date) or media.created_time > post_date:
      print "posting now, caption: " + caption
      client.create_photo('tedder42.tumblr.com', state='published', tags=['instagram'], source=media.images.get('standard_resolution').url, format='markdown', caption=('## ' + caption), date=media.created_time)

process_feed()
