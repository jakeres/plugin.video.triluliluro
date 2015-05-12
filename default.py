import codecs,urllib,urllib2,re,xbmc,xbmcplugin,xbmcaddon,xbmcgui,os,sys,commands,HTMLParser,jsunpack,time

website = 'http://www.trilulilu.ro/';

__version__ = "1.0.4"
__plugin__ = "trilulilu.ro" + __version__
__url__ = "www.xbmc.com"
settings = xbmcaddon.Addon( id = 'plugin.video.triluliluro' )

search_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'search.png' )
movies_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies.png' )
movies_hd_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies-hd.png' )
tv_series_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'tv.png' )
next_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'next.png' )


def ROOT():
    #addDir('Filme','http://www.trilulilu.ro/',1,movies_thumb)
    addDir('Cauta','http://www.trilulilu.ro/',3,search_thumb)
    addDir('Cauta ... dublat','http://www.trilulilu.ro/',31,search_thumb)
    
    xbmc.executebuiltin("Container.SetViewMode(500)")

def CAUTA_LIST(url):
    link = get_search(url)
                   
    match=re.compile('<a href="(http://www.trilulilu.ro/video-.+?)#ref=cauta" .+?title="(.+?)" .+?>\n.+?<div.+?>(\d+:\d+)</div><img (src|data-src)="(.+?)" width="', re.IGNORECASE|re.MULTILINE).findall(link)
    if len(match) > 0:
        print match
        for legatura, name, length, s, img in match:
            #name = HTMLParser.HTMLParser().unescape(  codecs.decode(name, "unicode_escape") ) + " " + length
            name = name + " " + length
            the_link = legatura
            image = img
            sxaddLink(name,the_link,image,name,10)

    match=re.compile('<link rel="next" href="\?offset=(\d+)" />', re.IGNORECASE).findall(link)
    if len(match) > 0:
      nexturl = re.sub('\?offset=(\d+)', '?offset='+match[0], url)
      if nexturl.find("offset=") == -1:
        nexturl += '?offset='+match[0]
      
      print "NEXT " + nexturl
      
      addNext('Next', nexturl, 2, next_thumb)
            
    xbmc.executebuiltin("Container.SetViewMode(500)")

def CAUTA(url, autoSearch = None):
    keyboard = xbmc.Keyboard( '' )
    keyboard.doModal()
    if ( keyboard.isConfirmed() == False ):
        return
    search_string = keyboard.getText()
    if len( search_string ) == 0:
        return
        
    if autoSearch is None:
      autoSearch = ""
    
    CAUTA_LIST( get_search_url(search_string + "" + autoSearch) )
    
    
def SXVIDEO_GENERIC_PLAY(sxurl, seltitle, linksource="source1"):
    listitem = xbmcgui.ListItem(seltitle)
    listitem.setInfo('video', {'Title': seltitle})

    selurl     = sxurl
    SXVIDEO_PLAY_THIS(selurl, listitem, None)
    
    return
      
def SXVIDEO_PLAY_THIS(selurl, listitem, source):

    movie_formats = {'flv': 'flv-vp6', 'mp4': 'mp4-360p'}
    sformat = ''
    player = xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ) 
    
    for (mfn, mf) in movie_formats.items():
      if SX_checkUrl(selurl + mf):
        player.play(selurl + mf, listitem)
        time.sleep(1)
        break;  
      #if player.isPlaying():
      #  break;
    
    try:
          print "-"
          #player.setSubtitles(source['subtitle'])
    except:
        pass

    #while player.isPlaying:
    #  xbmc.sleep(100);
      
    return player.isPlaying()


def SXSHOWINFO(text):
    #progress = xbmcgui.DialogProgress()
    #progress.create("kml browser", "downloading playlist...", "please wait.")
    print ""
    
def SXVIDEO_FILM_PLAY(url):
    SXSHOWINFO("Playing movie...")
    
    #print url 
    sxurli = sxGetMovieLink(url) 
    #print sxurli
    #return
    
    #print sxurls
    SXVIDEO_GENERIC_PLAY(sxurli['url'], sxurli['title'])
    
      
def SX_checkUrl(url):
    content_range=None
    try:
      req = urllib2.Request(url)
      #
      # Here we request that bytes 18000--19000 be downloaded.
      # The range is inclusive, and starts at 0.
      #
      req.headers['Range']='bytes=%s-%s' % (100, 200)
      f = urllib2.urlopen(req)
      # This shows you the actual bytes that have been downloaded.
      content_range=f.headers.get('Content-Range')
    except:
      pass
      
    print "URL costel " + url
    #print(content_range)
    
    return content_range != None

def sxGetMovieLink(url):
    print 'url video '+url
    #print 'nume video '+ name
    # thumbnail
    
    src = get_url(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    #print src
    
    thumbnail = ''
    title     = ''
    link_video_trilu = "" 
    
    
    #title
    match = re.compile('<title>(.+?)<', re.IGNORECASE).findall(src)
    title = HTMLParser.HTMLParser().unescape(match[0])
    title = re.sub('\s+-\s*Video\s*-\s*Trilulilu', '', title);
    #print "MATCH SERCH  " + match[0]
    
    #video link  --- # block_flash_vars = {"userid":"andreea_popa","hash":"edee1b51b240c9","server":"65","autoplay":"true","hasAds":"true","viewf
    match = re.compile('block_flash_vars = {"userid":"(.+?)","hash":"(.+?)","server":"(.+?)",', re.IGNORECASE).findall(src)
    if not match:
      #addLink('Could NOT generate video link ', " ", thumbnail, title)
      xbmc.executebuiltin('Notification(Error,Could NOT generate video link,5000,/script.hellow.world.png)')
      return False
    
    ids       = match[0]
    username  = ids[0]
    hash      = ids[1]
    server    = ids[2]
        
    #print "hash = " + hash + "; username = " + username + "; server=" + server
    
    # video id
    link_video_trilu = "http://fs"+server+".trilulilu.ro/stream.php?type=video&source=site&hash=" + hash + "&username=" + username + "&format="
        
    return {'url':link_video_trilu, 'title': title}

    
def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False
    
def get_search_url(keyword, offset = None):
    url = 'http://cauta.trilulilu.ro/video/' + urllib.quote_plus(keyword)
    
    if offset != None:
      url += "?offset="+offset
    
    return url

def get_search(url):
    
    params = {}
    req = urllib2.Request(url, urllib.urlencode(params))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def yt_get_all_url_maps_name(url):
    conn = urllib2.urlopen(url)
    encoding = conn.headers.getparam('charset')
    content = conn.read().decode(encoding)
    s = re.findall(r'"url_encoded_fmt_stream_map": "([^"]+)"', content)
    if s:
        s = s[0].split(',')
        s = [a.replace('\\u0026', '&') for a in s]
        s = [urllib2.parse_keqv_list(a.split('&')) for a in s]

    n = re.findall(r'<title>(.+) - YouTube</title>', content)
    return  (s or [], 
            HTMLParser.HTMLParser().unescape(n[0]))

def yt_get_url(z):
    #return urllib.unquote(z['url'] + '&signature=%s' % z['sig'])
    return urllib.unquote(z['url'])

def youtube_video_link(url):
    # 18 - mp4
    fmt = '18'
    s, n = yt_get_all_url_maps_name(url)
    for z in s:
        if z['itag'] == fmt:
            if 'mp4' in z['type']:
                ext = '.mp4'
            elif 'flv' in z['type']:
                ext = '.flv'
            found = True
            link = yt_get_url(z)
    return link

def sxaddLink(name,url,iconimage,movie_name,mode=4):
        ok=True
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": movie_name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addLink(name,url,iconimage,movie_name):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": movie_name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addNext(name,page,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        ROOT()

elif mode==2:
        CAUTA_LIST(url)
        
elif mode==3:
        CAUTA(url)

elif mode==31:
        CAUTA(url, " dublat")

elif mode==4:
        VIDEO(url,name)

elif mode==9:
        SXVIDEO_EPISOD_PLAY(url)

elif mode==10:
        SXVIDEO_FILM_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
