# -*- coding: utf-8 -*-
from __future__ import print_function
from future.standard_library import install_aliases

install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import itertools
import wikipedia
import smtplib
import feedparser

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
#define dictionaries for weather values. No need to create them evdry time a weather request comes in
startStr=" "

#vglobal variables

#api keys
musixmatchAPIKey=''
darSkiesApiKey=''

#dark skies
currently=""
minutely=""
hourly=""
daily=""
artistIDstr=""

#getNews
newsRequestUrl="https://www.rte.ie/news/rss/news-headlines.xml"
newsImg="https://lh3.googleusercontent.com/pq3O4a681DBih371ao6DE9v_I8kwyXGbuCXuUaKZSzUt0lgWR_cVE730ageVDzw_1gQ=w300"

#getEvents - establish mysql connection
import pymysql.cursors

# Connect to the database


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):

    if req.get("result").get("action")=="musixmatch-search-chart":
        country = req.get("result").get("parameters").get("chart-country").get("alpha-2")
        county_name = req.get("result").get("parameters").get("chart-country").get("name")
        country_nameStr=str(county_name)
        baseurl = "https://api.musixmatch.com/ws/1.1/chart.tracks.get?page=1&page_size=10&country="+country+"&apikey="+musixmatchAPIKey
        result = urlopen(baseurl).read()
        my_json = result.decode('utf8')
        data = json.loads(my_json)
        trackData=data.get("message").get("body").get("track_list")
        trackRes=[]
        for item in trackData:
            trackDetails=item
            trackName=trackDetails.get('track').get('track_name')
            trackArtist=trackDetails.get('track').get('artist_name')
            trackAlbum=trackDetails.get('track').get('album_name')
            trackList=("Song: "+trackName+"\nArtist: "+trackArtist+"\nAlbum: "+trackAlbum+"\n")
            trackRes.extend([trackList])
        trackResStr="\n".join(trackRes)
        return {
                "speech":"Here you go. Top 10 music charts for "+country_nameStr+". (In order 1 to 10).  :) \n\n"+trackResStr,
                "displayText":"Here you go. Top 10 music charts for "+country_nameStr+". (In order 1 to 10).  :) \n\n"+trackResStr,
                "source": "apiai-weather-webhook-sample"
                }

    if req.get("result").get("action")=="musixmatch-search-song":
        query_song = req.get("result").get("parameters").get("song-title")
        if " " in query_song:
            query_song=query_song.replace(" ","%20")
        baseurl = "https://api.musixmatch.com/ws/1.1/track.search?q_track="+query_song+"&s_artist_rating=desc&apikey="+musixmatchAPIKey
        result = urlopen(baseurl).read()
        my_json = result.decode('utf8')
        data = json.loads(my_json)

        #TO-DO - implement a check for no song found and respond with a string to the client.

        trackData=data.get("message").get("body").get("track_list")
        trackRes=[]
        for trackDetails in trackData:
            #trackDetails=item
            trackName=trackDetails.get('track').get('track_name')
            trackArtist=trackDetails.get('track').get('artist_name')
            trackArtistStr=str(trackArtist)
            trackAlbum=trackDetails.get('track').get('album_name')
            trackURL=trackDetails.get('track').get('track_share_url')
            trackImage=trackDetails.get('track').get('album_coverart_100x100')
            artistID=trackDetails.get('track').get('artist_id')
            artistIDstr=str(artistID)
            card = {
                	"title": "Song: " + trackName,
                	"subtitle": "Artist: " + trackArtist,
                	"buttons": [{
                    			"type": "web_url",
                    			"url": trackURL,
                    			"title": "View Lyrics"
                                },{
                                "type":"postback",
                                "title":"Show Albums",
                                "payload":"list albums for "+artistIDstr
                                },{
                                "type":"postback",
                                "title":"Similar Artisits",
                                "payload":"similar artists "+artistIDstr
                                }
                	]
                }
            trackRes.extend([card])
        response = {
            "speech": "You'll have to use Facebook Messenger to check album details. Sorry about that! :) ",
            "displayText": "You'll have to use Facebook Messenger to check album details. Sorry about that! :) ",
            "data":{
               "facebook" : {
                    "attachment" : {
                        "type" : "template",
                        "payload" : {
                            "template_type" : "generic",
                            "elements" :trackRes

                            }
                        }
                    }

                }
            }
        print(response)
        return response

    if req.get("result").get("action")=="musixmatch-similar-artists":
        similarArtistID=req.get("result").get("parameters").get("artistID")
        baseurl = "https://api.musixmatch.com/ws/1.1/artist.related.get?artist_id="+similarArtistID+"&apikey="+musixmatchAPIKey
        result = urlopen(baseurl).read()
        data = json.loads(result)
        similarData=data.get("message").get("body").get("artist_list")
        similarRes=[]
        for similarArtists in similarData:
            artistName=similarArtists.get('artist').get('artist_name')
            artistCountry=similarArtists.get('artist').get('artist_country')
            artistID=similarArtists.get('artist').get('artist_id')
            artistIDstr=str(artistID)
            card=card = {
                        "title": "Artist: " + artistName,
                        "subtitle": "Country: " + artistCountry,
                        "buttons": [{
                                    "type":"postback",
                                    "title":"Show Albums",
                                    "payload":"list albums for "+artistIDstr
                                    }
                        ]
                    }
            similarRes.extend([card])
        response = {
            "speech": "You'll have to use facebook messenger for this functionality. Sorry about that! :) ",
            "displayText": "You'll have to use facebook messenger for this functionality. Sorry about that! :)",
            "data":{
               "facebook" : {
                    "attachment" : {
                        "type" : "template",
                        "payload" : {
                            "template_type" : "generic",
                            "elements" :similarRes

                            }
                        }
                    }

                }
            }
        return response

    if req.get("result").get("action")=="musixmatch-get-artist-tracks":
        getArtistID= req.get("result").get("parameters").get("artistID")
        baseurl = "https://api.musixmatch.com/ws/1.1/artist.albums.get?artist_id="+getArtistID+"&s_release_date=desc&apikey="+musixmatchAPIKey
        result = urlopen(baseurl).read()
        data = json.loads(result)
        albumData=data.get("message").get("body").get("album_list")
        trackRes=[]
        for albumDetails in albumData:
            albumName=albumDetails.get('album').get('album_name')
            albumID=albumDetails.get('album').get('album_id')
            albumIDStr=str(albumID)
            albumTrackCount=albumDetails.get('album').get('album_track_count')
            albumReleaseDate=albumDetails.get('album').get('album_release_date')
            albumArtistName=albumDetails.get('album').get('artist_name')
            artistID=albumDetails.get('album').get('artist_id')
            artistIDstr=str(artistID)
            artistURL=albumDetails.get('album').get('album_edit_url')
            card = {
                    "title": "Album: " + albumName,
                    "subtitle": "Artist: " + albumArtistName,
                    "buttons": [{
                                "type": "web_url",
                                "url": artistURL,
                                "title": "Tracks on this album"
                                }
                    ]
                }
            trackRes.extend([card])
        response = {
            "speech": "You'll have to use facebook messenger for this functionality. Sorry about that! :) ",
            "displayText": "You'll have to use facebook messenger for this functionality. Sorry about that! :)",
            "data":{
               "facebook" : {
                    "attachment" : {
                        "type" : "template",
                        "payload" : {
                            "template_type" : "generic",
                            "elements" :trackRes

                            }
                        }
                    }

                }
            }

        return response

    if req.get("result").get("action")=="getjoke":
        baseurl = "http://api.icndb.com/jokes/random"
        result = urlopen(baseurl).read()
        data = json.loads(result)
        res = makeWebhookResultForGetJoke(data)
        return res

    if req.get("result").get("action")=="getBus":
        stopID = req.get("result").get("parameters").get("stopNum")
        print("stopID is:")
        print(stopID)
        baseurl = " https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?stopid="+stopID
        result = urlopen(baseurl).read()
        data = json.loads(result)
        res = makeWebhookResultForGetBus(data)
        return res

    if req.get("result").get("action")=="getDarkSkies":
        longitude = req.get("originalRequest").get("data").get("postback").get("data").get("long")
        longStr=str(longitude)
        latitude = req.get("originalRequest").get("data").get("postback").get("data").get("lat")
        latStr=str(latitude)
        baseurl="https://api.darksky.net/forecast/"+darSkiesApiKey+"/"+latStr+","+longStr+"?units=auto"
        result = urlopen(baseurl).read()
        data = json.loads(result)
        if not data.get('minutely'):
            minutely=("Sorry buddy, Looks like there's no data for the next hour's forecast for that location. Prepare for the worst and hope for the best I suppose!")
        else:
            minutely=data.get('minutely').get('summary')
        currently=data.get('currently').get('summary')
        hourly=data.get('hourly').get('summary')
        daily=data.get('daily').get('summary')
        currentlyStr=str(currently)
        minutelyStr=str(minutely)
        hourlyStr=str(hourly)
        dailyStr=str(daily)
        response="Here's the forecast now.....:) Make sure to check back again. Can be fierce changable. \n\nCurrently:\nLook out the window....Heyoooo!\n(ok, fine!...It's "+currentlyStr+")\n\nNext hour:\n"+minutely+"\n\nToday in General:\n"+hourlyStr+"\n\nRest of the Week:\n"+dailyStr+"\n\nPowered by DarkSky"
        return {
        #    for item in busList:
                "speech": response,
                "displayText":response,
                # "data": data,
                # "contextOut": [],
                "source": "apiai-weather-webhook-sample"
        }

    if req.get("result").get("action")=="getWiki":
        query = req.get("result").get("parameters").get("any")
        print (query)
        wikiSearch=wikipedia.search(query, results=5, suggestion=False)
        if not wikiSearch:
            wikiResponse="Sorry, I didnt find anything for that, can you check the spelling and try again? Thanks a mil!"
        else:
            wikiPage=wikipedia.page(query, auto_suggest=True)
            wikiURL=wikiPage.url
            wikiSum=wikipedia.summary(query,sentences=5,auto_suggest=True)
            wikiResponse=(wikiSum+"\n\nLearn more here: \n"+wikiURL)
        return {
        #    for item in busList:
                "speech":wikiResponse,
                "displayText":wikiResponse,
                # "data": data,
                # "contextOut": [],
                "source": "apiai-weather-webhook-sample"
        }

    if req.get("result").get("action")=="wiki-search":
        query = req.get("result").get("parameters").get("any")
        wikiSearch2=wikipedia.search(query, results=5, suggestion=False)
        option1 = wikiSearch2[0]
        option2 = wikiSearch2[1]
        option3 = wikiSearch2[2]
        option4 = wikiSearch2[3]
        option5 = wikiSearch2[4]
        response = {
            "speech": "Which one?",
            "displayText": "Which one?",
            "data":
                {"facebook":
                    {
                    "text": "I found these, which one would you like me to get info on?",
                    "quick_replies":
                        [

                            {
                            "content_type": "text",
                            "title": option1,
                            "payload": "tell me about "+option1
                            },
                            {
                            "content_type": "text",
                            "title": option2,
                            "payload": "tell me about "+option2
                            },
                            {
                            "content_type": "text",
                            "title": option3,
                            "payload": "tell me about "+option3
                            },
                            {
                            "content_type": "text",
                            "title": option4,
                            "payload": "tell me about "+option4
                            },
                            {
                            "content_type": "text",
                            "title": option5,
                            "payload": "tell me about "+option5
                            },

                        ]
                    }
                }
            }
        return response

    if req.get("result").get("action")=="getNews":
        print("newsCategory==============")
        newsCategory = req.get("result").get("parameters").get("newsCategory")
        newsCategoryStr=str(newsCategory)
        print("start if elif========================s")
        if newsCategoryStr == "sports":
            newsRequestUrl='http://www.rte.ie/rss/sport.xml'
            newsImg="https://pbs.twimg.com/profile_images/588375673422635010/LE_CyqIy.png"
        elif newsCategoryStr == 'entertainment':
            newsRequestUrl = "http://www.dailymail.co.uk/tvshowbiz/index.rss"
            newsImg="https://assets.materialup.com/uploads/4f5118c7-ca50-4ce7-941f-bd6825fbdb72/avatar.jpg"
        elif newsCategoryStr == 'business':
            newsRequestUrl = "https://www.rte.ie/news/rss/business-headlines.xml"
            newsImg="https://img.rasset.ie/00037501-600.jpg"
        elif newsCategoryStr == 'gaa':
            newsRequestUrl = "http://www.rte.ie/rss/gaa.xml"
            newsImg="https://pbs.twimg.com/profile_images/588375673422635010/LE_CyqIy.png"
        elif newsCategoryStr == 'nuacht':
            newsRequestUrl = "https://www.rte.ie/news/rss/nuacht.xml"
            newsImg="https://img.rasset.ie/000c397e-880.jpg"
        elif newsCategoryStr == 'rugby':
            newsRequestUrl = "http://www.rte.ie/rss/rugby.xml"
            newsImg="https://pbs.twimg.com/profile_images/588375673422635010/LE_CyqIy.png"
        elif newsCategoryStr == 'racing':
            newsRequestUrl = "http://www.rte.ie/rss/racing.xml"
            newsImg="https://pbs.twimg.com/profile_images/588375673422635010/LE_CyqIy.png"
        elif newsCategoryStr == 'headlines':
            newsRequestUrl = "https://www.rte.ie/news/rss/news-headlines.xml"
            newsImg="https://lh3.googleusercontent.com/pq3O4a681DBih371ao6DE9v_I8kwyXGbuCXuUaKZSzUt0lgWR_cVE730ageVDzw_1gQ=w300"
        print("end if elif")
        print("newsRequestUrl===============")
        print(newsRequestUrl)
        print("feedparser url====================")
        feed=feedparser.parse(newsRequestUrl)
        print(feed)
        print("title=============")
        title=feed['feed']['title']
        print(title)
        newsRes=[]
        index=0
        print("start for loop =========================")
        for item in feed['entries']:
            title=item['title']
            titleStr=str(title)
            summary=item['summary']
            summaryStr=str(summary)
            published=item['published']
            publishedStr=str(published)
            link=item['link']
            linkStr=str(link)
            print(link)
            #media_content = item['media_content']
            #for item in media_content:
            #    imgURL=item['url']
            #    print("imgURL=============")
            #    print(imgURL)
            index=index+1
            newsCard = {
                        "title": title,
                        "subtitle": summary,
                        "image_url":newsImg,
                        "buttons": [
                                    {
                                    "type": "web_url",
                                    "title": "View Article",
                                    "url":link
                                    }
                                   ]
                        }
            print("card=======")
            print(newsCard)
            newsRes.extend([newsCard])
            print("index==============")
            print(index)
            if index == 10:
                break

        print("end for loop =========================")
        print("final response")
        newsResponse={
            "speech": "Facebook News ",
            "displayText": "Facebook News ",
            "data":{
               "facebook" : {
                    "attachment" : {
                        "type" : "template",
                        "payload" : {
                            "template_type" : "generic",
                            "elements" : newsRes

                                    }
                            }
                        }
                    }
                }

        print(newsResponse)
        return newsResponse

    if req.get("result").get("action")=="getEvents":
        eventDate = ""#req.get("result").get("parameters").get("stopNum")
        eventVenue = ""
                                     user='',
                                     password='',
                                     db='',
                                     charset='',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `bonners2_dublinbot`.`events` where `location` like '%button%'"
                cursor.execute(sql)
                result = cursor.fetchall()
                print(result)
        finally:
            connection.close()
        #format result

        #send results back to user
        eventresult={
        #    for item in busList:
                "speech":"events SQL",
                "displayText":"events SQL",
                # "data": data,
                # "contextOut": [],
                "source": "apiai-weather-webhook-sample"
        }

        return eventResult

def makeWebhookResultForGetBus(data):

    busList=[]
    for item in data['results']:
        busDest=item['destination']
        busDestStr = "".join(busDest)
        busRoute=item['route']
        busRouteStr = "".join(busRoute)
        busDueTime=item['duetime']
        busDueTimeStr = "".join(busDueTime)
        busItemStr=("The "+busRouteStr+" to "+busDestStr+" arrives in: "+busDueTimeStr+" min")
        busList.extend([busItemStr])
    busListStr = "\n".join(busList)
    return {
    #    for item in busList:
            "speech": busListStr,
            "displayText": busListStr,
            # "data": data,
            # "contextOut": [],
            "source": "apiai-weather-webhook-sample"
    }

def makeWebhookResultForGetJoke(data):
    print("getjokeResult is:")
    print (data)
    valueString = data.get('value')
    joke = valueString.get('joke')
    speechText = joke
    displayText = joke
    return {
        "speech": speechText,
        "displayText": displayText,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
