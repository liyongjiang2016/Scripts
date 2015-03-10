#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from HTMLParser import HTMLParser
import urllib, json

import common, db

def Start(db_, artist_list):

    GetSongs_URL_Template_ = 'http://music.baidu.com/data/user/getsongs?start=%s&ting_uid=%s'
    SongLink_URL_Template_ = 'http://play.baidu.com/data/music/songlink?songIds=%s'
    PRE_URL_ = 'http://play.baidu.com'

    Find_Song_Switch_ = False
    Artist_Id_ = ''

    def Find_Song_Link(tag, attrs):
        global Find_Song_Switch_
        try:
            if tag == 'a':
                for k, v in attrs:
                    if(k and k == 'href' and v and v.find('/song/') != -1):
                        href_ = v[v.find('/song/') + len('/song/'):]
                        if href_.find('/') != -1:
                            href_ = href_[:href_.find('/')]
                        #Song_List_.add(href_)
                        raw_content = common.http_read(SongLink_URL_Template_ % href_)
                        raw_object = json.loads(raw_content)
                        songList = raw_object['data']['songList']
                        if len(songList) > 0:
                            song_ = songList[0]
                            songId = song_['songId']
                            songName = song_['songName']
                            lrclink = PRE_URL_ + song_['lrcLink']
                            songlink = song_['songLink']
                            rate = song_['rate']
                            size = song_['size']
                            artist_id = Artist_Id_
                            db_.add_song(songId, songName, lrclink, songlink, rate, size, artist_id)
                            print 'song %d has been saved.' % songId
                        Find_Song_Switch_ = True
        except Exception, e:
            common.log('Find_Song_Link: ' + e)
    
    parser = HTMLParser()
    parser.handle_starttag = Find_Song_Link
    
    for k_ in artist_list:
        print 'start process artist %s ...' % k_
        s_ = 0
        Find_Song_Switch_ = True
        while(Find_Song_Switch_):
            Find_Song_Switch_ = False
            raw_content = common.http_read(GetSongs_URL_Template_ % (s_, k_))
            s_ = s_ + 25
            try:
                raw_object = json.loads(raw_content)
            except Exception, e:
                common.log('json.loads: ' + e)
            try:
                raw_content = raw_object['data']['html']
            except Exception, e:
                common.log('extract html from json object: ' + e)
            try:
                raw_content = raw_content.decode('unicode_escape')
            except Exception, e:
                common.log('str.decode: ' + e) 
            try:
                Artist_Id_ = k_
                parser.feed(raw_content)
                db_.add_artist_log(k_)
            except Exception, e:
                common.log('HTMLParser.feed: ' + e)
    
    return True    





