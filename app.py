# -*- coding: utf-8 -*-
from __future__ import print_function
from future.standard_library import install_aliases
from PyLyrics import *

install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import itertools
import wikipedia
import smtplib

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
#define dictionaries for weather values. No need to create them evdry time a weather request comes in
dictTemp=({ '-28':'ridiculously cold! You shouldnt have your phone out in such temperature.','-27':'ridiculously cold! You shouldnt have your phone out in such temperature.','-26':'ridiculously cold! You shouldnt have your phone out in such temperature.','-25':'ridiculously cold! You shouldnt have your phone out in such temperature.','-24':'ridiculously cold! You shouldnt have your phone out in such temperature.','-23':'ridiculously cold! You shouldnt have your phone out in such temperature.','-22':'ridiculously cold! You shouldnt have your phone out in such temperature.','-21':'ridiculously cold! You shouldnt have your phone out in such temperature.','-20':'too cold. Why would you do this to yourself!?','-19':'too cold. Why would you do this to yourself!?','-18':'too cold. Why would you do this to yourself!?','-17':'too cold. Why would you do this to yourself!?','-16':'too cold. Why would you do this to yourself!?','-15':'too cold. Why would you do this to yourself!?','-14':'too cold. Why would you do this to yourself!?','-13':'too cold. Why would you do this to yourself!?','-12':'bearable out, but Id rather not be in such coldness!','-11':'bearable out, but Id rather not be in such coldness!','-10':'bearable out, but Id rather not be in such coldness!','-9':'bearable out, but Id rather not be in such coldness!','-8':'bearable out, but Id rather not be in such coldness!','-7':'bearable out, but Id rather not be in such coldness!','-6':'bearable out, but Id rather not be in such coldness!','-5':'positively freezing!!','-4':'positively freezing!!','-3':'positively freezing!!','-2':'bleedin baltic!!','-1':'positively freezing!!','0':'fairly chilly now. Get yer hats and scarves on!','1':'fairly chilly now. Get yer hats and scarves on!','2':'fairly chilly now. Get yer hats and scarves on!','3':'fairly chilly now. Get yer hats and scarves on!','4':'fairly chilly now. Get yer hats and scarves on!','5':'chilly enough now','6':'chilly enough now','7':'chilly enough now','8':'chilly enough now','9':'chilly enough now','10':'getting nice and warm now not quite shorts and t-shirt weather though.','11':'getting nice and warm now not quite shorts and t-shirt weather though.','12':'getting nice and warm now not quite shorts and t-shirt weather though.','13':'getting nice and warm now not quite shorts and t-shirt weather though.','14':'lovely and warm now!','15':'lovely and warm now!','16':'lovely and warm now!','17':'lovely and warm now!','18':'lovely and warm now!','19':'lovely and warm now!','20':'time to get the sun cream out....and the 99s!','21':'time to get the sun cream out....and the 99s!','22':'time to get the sun cream out....and the 99s!','23':'time to get the sun cream out....and the 99s!','24':'time to get the sun cream ou....and the 99s!','25':'time to get the sun cream out....and the 99s!','26':'nice and toasty. delightful :)','27':'nice and toasty. delightful :)','28':'nice and toasty. delightful :)','29':'nice and toasty. delightful :)','30':'nice and toasty. delightful :)','31':'above 30. Its seriously hot now. I would be burnt to a crisp in this heat!','32':'above 30. Its seriously hot now. I would be burnt to a crisp in this heat!','33':'above 30. Its seriously hot now. I would be burnt to a crisp in this heat!','34':'above 30. Its seriously hot now. I would be burnt to a crisp in this heat!','35':'above 30. Its seriously hot now. I would be burnt to a crisp in this heat!','36':'mad hot. Get back inside to the air conditioning ye mad yoke. Fierce hot altogether.','37':'mad hot. Get back inside to the air conditioning ye mad yoke. Fierce hot altogether.','38':'mad hot. Get back inside to the air conditioning ye mad yoke. Fierce hot altogether.','39':'mad hot. Get back inside to the air conditioning ye mad yoke. Fierce hot altogether.','40':'40. I was in 40 degree......once, never again!. Pasty irish skin cant handle this sort of intensity','41':'mad hot. Get back inside to the air conditioning ye mad yoke. Fierce hot altogether.','42':'mad hot. Get back inside to the air conditioning ye mad yoke. Fierce hot altogether.','43':'too hot to even walk to the shop. Better get a taxi insead.','44':'too hot to even walk to the shop. Better get a taxi insead.','45':'too hot to even walk to the shop. Better get a taxi insead.','46':'too hot to even walk to the shop. Better get a taxi insead.','47':'too hot to even walk to the shop. Better get a taxi insead.','48':'too hot to even walk to the shop. Better get a taxi insead.','49':'too hot to even walk to the shop. Better get a taxi insead.','50':'50. Get up the yard. Why would you go where its 50?','51':'dangerous heat levels now. Down with this sort of thing.','52':'dangerous heat levels now. Down with this sort of thing.','53':'dangerous heat levels now. Down with this sort of thing.','54':'dangerous heat levels now. Down with this sort of thing.','55':'dangerous heat levels now. Down with this sort of thing.','56':'almost at 60 degrees....why....whywhywhy. Stay inside ye mad eejit you.','57':'almost at 60 degrees....why....whywhywhy. Stay inside ye mad eejit you.','58':'almost at 60 degrees....why....whywhywhy. Stay inside ye mad eejit you.','59':'almost at 60 degrees....why....whywhywhy. Stay inside ye mad eejit you.','60':'60, go wan ta fuck!'})
dictID=({ '200':'thunderstorms and light rain, might see a light show if yer lucky.','201':'thunderstorms and rain.','202':'thunderstorms and heavy rain. Jaysus, almost a monsoon.','210':'light thunderstorms.','211':'thunderstorms. 5 seconds per mile isnt it?','212':'heavy thunderstorms. Careful now!','221':'ragged thunderstorms. Im not even sure what that is to be honest.','230':'thunderstorms and light drizzle.','231':'thunderstorms and drizzle. Only spittin sure!','232':'thunderstorms with heavy drizzle.','300':'light intensity drizzle, sure its only spittin. Be grand!','301':'drizzle, sure its only spittin.','302':'heavy intensity drizzle, pure soft day out. Lovely.','310':'light intensity drizzle rain, a soft aul day.','311':'drizzle rain. There ye are now, irish weather in a nutshell. Drizzle rain','312':'heavy intensity drizzle rain','313':'shower rain and drizzle','314':'heavy shower rain and drizzle','321':'shower drizzle....what even is that!?','500':'light rain','501':'moderate rain','502':'heavy intensity rain. Bring an umbrella.','503':'very heavy rain, wetter than an otters pocket!','504':'extreme rain, Ill give you a tenner if you run out in that in your socks. ','511':'freezing rain','520':'light intensity shower rain','521':'shower rain','522':'heavy intensity shower rain','531':'ragged shower rain','600':'light snow. Sorry, it aint gonna stick','601':'snow','602':'heavy snow, and a chance for snowmen!','611':'sleet....sleet is fairly shite isnt it!?','612':'shower sleet','615':'light rain and snow, get ready for some sludge! hahaha. ','616':'rain and snow','620':'light shower snow','621':'shower snow','622':'heavy shower snow','701':'some mist.','711':'smoke. Someone have a fire going!? wha?','721':'haze','731':'sand, dust whirls','741':'fog, careful out on the seas there','751':'sand, dust whirls','761':'dust','762':'volcanic ash','771':'squalls','781':'tornado','800':'clear skies','801':'a few clouds','802':'some scattered clouds','803':'broken clouds','804':'overcast clouds','900':'a tornado......find a safe place quick! :) ','901':'a tropical storm','902':'a hurricane','903':'pretty cold weather in general','904':'fairly hot weather on the whole','905':'windy weather in general','906':'hail stones','951':'generally calm weather....for now anyway','952':'light breeze','953':'a gentle breeze','954':'a moderate breeze','955':'a fresh breeze','956':'a strong breeze','957':'a high wind, near gale','958':'a gale','959':'a severe gale','960':'a proper storm','961':'a violent storm, watch out, careful now','962':' a hurricane.....if you need me to tell you to get inside, then...well....get inside',})
dictWind=({ '1':'dead wind, practically no wind at all','2':'light air, barely a breeze at all','3':'light air, barely a breeze at all','4':'light air, barely a breeze at all','5':'light air, barely a breeze at all','6':'light breeze. Nice and fresh.','7':'light breeze. Nice and fresh.','8':'light breeze. Nice and fresh.','9':'light breeze. Nice and fresh.','10':'light breeze. Nice and fresh.','11':'light breeze. Nice and fresh.','12':'gentle breeze, thats lovely now.','13':'gentle breeze','14':'gentle breeze, I like a little wind like this.','15':'gentle breeze. Cmere to me.....go on :P','16':'gentle breeze, thats lovely now.','17':'gentle breeze','18':'gentle breeze, thats lovely now.','19':'gentle breeze','20':'moderate reeze','21':'moderate reeze','22':'moderate reeze','23':'moderate reeze','24':'moderate reeze','25':'moderate reeze','26':'moderate reeze','27':'moderate reeze','28':'moderate reeze','29':'fresh breeze','30':'fresh breeze, blow the cobwebs away :) ','31':'fresh breeze, blow the cobwebs away :) ','32':'fresh breeze, blow the cobwebs away :) ','33':'fresh breeze, tis only whopper i think...not too windy like!','34':'fresh breeze','35':'fresh breeze','36':'fresh breewze, tis only whopper i think...not too windy like!','37':'fresh breeze','38':'fresh breeze','39':'strong breeze','40':'strong breeze, getting a bit on the windy side now.','41':'strong breeze, getting a bit on the windy side now.','42':'strong breeze, pretty windy now. Keep hold of yer hat!','43':'strong breeze, pretty windy now. Keep hold of yer hat!','44':'strong breeze, ye wont be blown over or anything, but sure be careful anyway!','45':'strong breeze, ye wont be blown over or anything, but sure be careful anyway!','46':'strong breeze','47':'strong breeze, ye wont be blown over or anything, but sure be careful anyway!','48':'strong breeze','49':'strong breeze, pretty windy now. Keep hold of yer hat!','50':'high wind, might be worth leaving the umbrella at home. itll probably break','51':'high wind','52':'high wind, might be worth leaving the umbrella at home. itll probably break','53':'high wind','54':'high wind, thats a pretty fast wind...watch out.','55':'high wind, thats a pretty fast wind...watch out.','56':'high wind, right, thats a pretty strong wind we have going. Sure you can nearly take off! hahaha.','57':'high wind, right, thats a pretty strong wind we have going. Sure you can nearly take off! hahaha.','58':'high wind, right, thats a pretty strong wind we have going. Sure you can nearly take off! hahaha.','59':'high wind, right, thats a pretty strong wind we have going. Sure you can nearly take off! hahaha.','60':'high wind, right, thats a pretty strong wind we have going. Sure you can nearly take off! hahaha.','61':'high wind','62':'gale force wind, very high wind altogether!','63':'gale force wind, very high wind altogether!','64':'gale force wind, very high wind altogether!','65':'gale force wind, very high wind altogether!','66':'gale force wind, very high wind altogether!','67':'gale force wind, very high wind altogether!','68':'gale force, would ye schtop....68Kph!!','69':'gale force wind! Careful now, down with this sort of thing!','70':'gale force, very high wind','71':'gale force, very high wind','72':'gale force, very high wind','73':'gale force, very high wind','74':'gale force, very high wind','75':'strong gale','76':'strong gale','77':'strong gale','78':'strong gale','79':'strong gale','80':'strong gale. 80Kph....ive never even experienced such a thing. Whats it like?','81':'strong gale','82':'strong gale','83':'strong gale, beyond fierce windy as they say','84':'strong gale, beyond fierce windy as they say','85':'strong gale, beyond fierce windy as they say','86':'strong gale, beyond fierce windy as they say','87':'strong gale, beyond fierce windy as they say','88':'strong gale','89':'Storm, really high gale force winds now','90':'Storm, really high gale force winds now. ','91':'Storm, really high gale force winds now. ','92':'Storm, really high gale force winds. You should really be indoors at this stage ','93':'Storm, really high gale force winds ','94':'Storm, really high gale force winds. You should really be indoors at this stage ','95':'Storm, really high gale force winds. You should really be indoors at this stage ','96':'Storm, really high gale force winds. You should really be indoors at this stage ','97':'Storm, really high gale force winds ','98':'Storm, really high gale force winds ','99':'Storm, really high gale force winds ','100':'Storm, really high gale force winds ','101':'Storm, really high gale force winds ','102':'Storm, really high gale force winds ','103':'violent storm, practically a hurricane','104':'violent storm, practically a hurricane','105':'violent storm, practically a hurricane','106':'violent storm, practically a hurricane','107':'violent storm, practically a hurricane','108':'violent storm, practically a hurricane','109':'violent storm, practically a hurricane','110':'violent storm, practically a hurricane','111':'violent storm, practically a hurricane','112':'violent storm, practically a hurricane','113':'violent storm, practically a hurricane','114':'violent storm, practically a hurricane','115':'violent storm, practically a hurricane','116':'violent storm, practically a hurricane','117':'violent storm, practically a hurricane','118':'hurricane. Youre in a hurricane. Are you happy with yourself!','119':'bleedin hurricane! run away!!','120':'hurricane with 120Kph wind!! Fook sakes....gerrup the yard with that!','121':'hurricane','122':'hurricane','123':'hurricane...gerrup. Stay inside if you can!','124':'hurricane...gerrup. Stay inside if you can!','125':'hurricane. As the resident chatbot, I recommend you stay inside....probably....im just a chatbot.','126':'hurricane','127':'hurricane','128':'hurricane! I reckon this one could do with being told to Jog right on!!','129':'hurricane! I reckon this one could do with being told to Jog right on!!',})
startStr=" "
musixmatchAPIKey=<musixmatch api key>
apiKey=<OWM api key>

artistIDstr=""
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
                "speech":"Here you go. Top 10 music charts for "+country_nameStr+". (In order 1 to 10). G'wan to me! :) \n\n"+trackResStr,
                "displayText":"Here you go. Top 10 music charts for "+country_nameStr+". (In order 1 to 10). G'wan to me! :) \n\n"+trackResStr,
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
            print("card info ========================")
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
                                "payload":"show similar "+artistIDstr
                                }
                	]
                }
            print(card)
            print("trackRes====================")
            trackRes.extend([card])
            print(trackRes)
        print("startResponse======================")
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

        return response

    if req.get("result").get("action")=="musixmatch-get-artist-tracks":
        print("GETartistID=======================")
        getArtistID= req.get("result").get("parameters").get("artistID")
        print(getArtistID)
        baseurl = "https://api.musixmatch.com/ws/1.1/artist.albums.get?artist_id="+getArtistID+"&s_release_date=desc&apikey="+musixmatchAPIKey
        result = urlopen(baseurl).read()
        data = json.loads(result)
        print("data=============")
        print(data)
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
            print("album card info ========================")
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
            print(card)
            print("albumRes====================")
            trackRes.extend([card])
        print(trackRes)
        print("startAlbum-Response======================")
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

    if req.get("result").get("action")=="getOWM":
        city = req.get("result").get("parameters").get("cities")
        baseurl="http://api.openweathermap.org/data/2.5/weather?id="+city+"&units=metric&APPID="+apiKey
        result = urlopen(baseurl).read()
        data = json.loads(result)
        res = makeWebhookResultForGetOWM(data)
        return res

    if req.get("result").get("action")=="lyrics-album-search":
        singer = req.get("result").get("parameters").get("artist-name")
        albumList=[]
        albums = PyLyrics.getAlbums(singer=singer)
        print(albums)
        for a in albums:
            print(a)
            aStr=str(a)
            albumList.extend([aStr])
        albumResult = "\n".join(albumList)
        print(albumResult)
        return {
        #    for item in busList:
                "speech":"Here you go. These are the albums by "+singer+"\n\n"+albumResult,
                "displayText":"Here you go. These are the albums by "+singer+"\n\n"+albumResult,
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


def makeWebhookResultForGetOWM(data):

##current weather

    temp=data['main']['temp']    #get the general temperature from the response. Max and Min are available, but these are not needed
    tempint=int(round(temp)) # round the decimal value to a single whole number
    tempStr=str(tempint) # convert to string for use in response
    weatherCity=data['name']#get the city name, to e used in the response to client
    humidity=data['main']['humidity']    #get humidity from response
    humidityStr=str(humidity)   #convert humid value to string
    windSpeed=data['wind']['speed'] # get windspeed
    windSpeedint=int(round(windSpeed)) # convert windspeed to an int and round it up/down
    windSpeedStr=str(windSpeedint) #convert rounded int to string so it can be used in the response to client
    weatherID1=data['weather'][0]['id'] #get the weather ID number
    weatherID1str=str(weatherID1) # convert the Id number to a string to be used in dictionary lookup

#forecast weather e.g tomorrow. limit of 5 day forecase



##form a response
    #get values in order to create sentence
    idResp=dictID[(weatherID1str)] # get value from ID dictionary. Results in a string
    tempResp=dictTemp[(tempStr)] # get value from temperature dictionary. Results in a string
    windResp=dictWind[(windSpeedStr)] # get value from wind dictionary. Results in a string

    #Create a sentence using the dictionary values. This is returned to the client as a "weather blurb" before the detailed weather data
    startStr=("It's "+tempResp+" With "+idResp+" and a "+windResp)
    #form the final response to the client
    weatherResp=(startStr+"\n\nToday in "+weatherCity+":\nTemperature: "+tempStr+" deg\nHumidity: "+humidityStr+"%\nWind: "+windSpeedStr+" kph")
    return {
    #    for item in busList:
            "speech":weatherResp,
            "displayText":weatherResp,
            # "data": data,
            # "contextOut": [],
            "source": "apiai-weather-webhook-sample"
    }

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
