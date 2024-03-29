#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib2, json, re, urllib, os, uuid, contextlib, zipfile, random, base64, time, thread, socket, xbmcplugin, xbmc, xbmcgui, xbmcaddon, xbmcvfs, traceback, cookielib, json, sys, requests, resolveurl, js2py
from datetime import datetime
from urlresolver.plugins.lib import jsunpack
from xml.sax.saxutils import escape
from contextlib import contextmanager
#from resources.libs import GATracker, extract, downloader, skinSwitch, wizard as wiz

#Enable inputstream.adaptive
@contextmanager
def enabled_addon(addon):
    data = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","params":{"addonid":"'+addon+'","properties":["enabled","installed"]},"id":5}'))
    if "result" in data:
        xbmc.log('Add-on InputStream Adaptive installed',xbmc.LOGNOTICE)
        if data["result"]["addon"]["enabled"]:
            xbmc.log('Add-on InputStream Adaptive enabled',xbmc.LOGNOTICE)
        else:
            xbmc.log('Add-on InputStream Adaptive enabling',xbmc.LOGNOTICE)
            result_enabled = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"'+addon+'","enabled":true},"id":9}')
            xbmc.log('Add-on InputStream Adaptive enabled',xbmc.LOGNOTICE)
    else:
        xbmc.log('Add-on InputStream Adaptive not installed',xbmc.LOGNOTICE)
    yield

def run():
    with enabled_addon("inputstream.adaptive"):
        addon = xbmcaddon.Addon("plugin.video.vinh.movies")
run()

#Open youtubbe settings to enable MPEG-Dash to play youtube live
'''yt_addon = xbmcaddon.Addon('plugin.video.youtube')
if yt_addon.getSetting('kodion.video.quality.mpd') != 'true':
	dialog = xbmcgui.Dialog()
	yes = dialog.yesno(
		'This Channel Need to Enable MPEG-DASH to Play!\n',
		'[COLOR yellow]Please Click OK, Choose MPEG-DASH -> Select Use MPEG-DASH -> Click OK[/COLOR]',
		yeslabel='OK',
		nolabel='CANCEL'
		)
	if yes:
		yt_settings = xbmcaddon.Addon('plugin.video.youtube').openSettings()
		xbmc.executebuiltin('yt_settings')
else: 
    addon = xbmcaddon.Addon("plugin.video.vinh.movies")'''


# Tham khảo xbmcswift2 framework cho kodi addon tại
# http://xbmcswift2.readthedocs.io/en/latest/
from kodiswift import Plugin, xbmc, xbmcaddon, xbmcgui, actions
path = xbmc.translatePath(
	xbmcaddon.Addon().getAddonInfo('path')).decode("utf-8")
cache = xbmc.translatePath(os.path.join(path, ".cache"))
tmp = xbmc.translatePath('special://temp')
addons_folder = xbmc.translatePath('special://home/addons')
image = xbmc.translatePath(os.path.join(path, "icon.png"))

plugin = Plugin()
addon = xbmcaddon.Addon("plugin.video.vinh.movies")
pluginrootpath = "plugin://plugin.video.vinh.movies"
http = httplib2.Http(cache, disable_ssl_certificate_validation=True)
query_url = "https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?gid={gid}&headers=1&tq={tq}"
sheet_headers = {
	"User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.3; WOW64; Trident/7.0)",
	"Accept-Encoding": "gzip, deflate, sdch"
}

apk = xbmc.getCondVisibility('system.platform.android')

def GetSheetIDFromSettings():
	sid = '1pLac4rIGw6xFBPisH84zMr799JO41NVFGyW6rT1ZMHA'
	resp, content = http.request(get_fshare_setting("GSheetURL"), "HEAD")
	try:
		sid = re.compile("/d/(.+?)/").findall(resp["content-location"])[0]
	except:
		pass
	return sid

def SEARCHToItems(url_path=''):
	headers2 = {
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
		'Referer':url_path,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	}

	if 'swiftstreamz.com' in url_path:		
		item_re = 'cat_id":"29",(.*?,)(.*?,)(.*?),"channel_desc'
		(resp, content) = http.request(
			url_path, "GET",
			headers=sheet_headers
		)
		items = []
		matchs = re.compile(item_re).findall(content)
		for label,path,thumb in matchs:
			if "channel_title" in label:
				label = re.compile('channel_title\":\"(.*?)"').findall(label)[0]
			if "channel_url" in path:
				path = re.compile('channel_url\":\"(.*?)"').findall(path)[0]
				linkstream = 'plugin://script.module.streamhublive/play/?url=swift:'+path+'&mode=10&quot'
			if "channel_thumbnail" in thumb:
				thumb = re.compile('channel_thumbnail\":\"(.*?)"').findall(thumb)[0]
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": linkstream.strip(),
			}
			#Xong go to def play_url
			item["path"] = pluginrootpath + \
					"/play/%s" % urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	elif url_path.startswith('http://topphimhd.com'):
		keyb = plugin.keyboard(heading = 'Tìm kiếm')
		if keyb:
			url_path = "http://topphimhd.com/search/%s" % keyb
			return M3UToItems(url_path=url_path)
		else:
			#url_path = "http://topphimhd.com/search/monkey"
			return None
		return M3UToItems(url_path=url_path)

@plugin.route('/search/<path>/<tracking_string>')
def SEARCH(path="0", tracking_string="SEARCH"):
	GA(  # tracking
		"SEARCH - %s" % tracking_string,
		"/search/%s" % path
	)

	items = SEARCHToItems(path)
	return plugin.finish(AddTracking(items))

def Layer2ToItems(url_path=""):
	headers2 = {
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
		'Referer':url_path,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	}

#	if 'sublink' in url_path:
#		if '(' in url_path:
#			url = re.compile('<sublink>(.*?)\(.*?</sublink>').findall(url_path)[:] #for builds.kodiuk.tv
#		else:
#			url = re.compile('<sublink>(.*?)</sublink>').findall(url_path)[:]
#		i = len(url)
#		links = ['Link'] * i
#		links2 = []
#		for item in links:
#			item = item + ' ' + str(i)
#			i = i - 1
#			links2 += [item]
#		links2.reverse()
#		dialog = xbmcgui.Dialog()
#		choise = dialog.select('Please Choose a Link - Xin Chọn Link', links2)
#		#return plugin.set_resolved_url(url[choise])
#		return play_url(url[choise])
####
##	if 'sublink' in url_path:
##		if '(' in url_path:
##			url_path = re.compile('<sublink>(.*?)\(.*?</sublink>').findall(url_path)[:] #for builds.kodiuk.tv
##		else:
##			url_path = re.compile('<sublink>(.*?)</sublink>').findall(url_path)[:]
#		items = [] # for look
#		for path in url_path:
#			if path.startswith('http://dl.upload10') or path.startswith('http://dl2.upload10'):
#				path = pluginrootpath + "/layer2/" + urllib.quote_plus(path) #useless for look only
#			else:
#				path = path
#			items += [path]
#		dialog = xbmcgui.Dialog()
#		choise = dialog.select('Please Choose a Link - Xin Chọn Link', items)
##		dialog = xbmcgui.Dialog()
##		choise = dialog.select('Please Choose a Link - Xin Chọn Link', url_path) #url_path is a list, choise is 0, 1, 2, ...
##		if choise == -1: #choose cancel
##			#return None
##			pass
##		else:
##			if url_path[choise].startswith('http://dl.upload10') or url_path[choise].startswith('http://dl2.upload10'): #url_path[choise] is url_path first or second .. in the list
##				return Layer2ToItems(url_path[choise])
##			elif url_path[choise].startswith('https://clipwatching.com') or url_path[choise].startswith('https://vidlox.me'):
##				return play_url(url_path[choise])
##			else:
##				return play_url(url_path[choise]) #will get error get addtracking, bc direct link(not list anything) ??
	
	if url_path.startswith('https://bilutvz.com') or url_path.startswith('https://bilumoi.com') or url_path.startswith('https://zingtvz.org'): #layer2
		source = requests.get(url_path, headers=headers2).text
		url_vs = re.findall('btn-danger" href="(.*?)"', source)[0] #vietsub
		content_vs = requests.get(url_vs, headers=headers2).content
		try: #Thuyet Minh if available
			url_tm = re.findall('class="playing".*?href="(.*?)"', content_vs)[0]
			content_tm = requests.get(url_tm, headers=headers2).content
		except: #if not
			content_tm = ''
		#item_re = '<a id=".*?href="(.*?)".*?title="(.*?)"'
		item_re = '<a id="ep.*?href="(.*?)".*?title="(.*?)"'
		content_all = content_vs+content_tm
		#thumb = re.findall('image" content="fsdf(.*?)"', content_vs)[0]
		matchs_all = re.compile(item_re).findall(content_all)
		items = []
		for path, label in matchs_all:
			try:
				thumb = re.findall('image" content="(https://zingtvz.org.*?)"', content_vs)[0]
			except:
				thumb = ''
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	#if url_path.startswith('http://topphimhd.com/') or url_path.startswith('http://topphimhdz.com') or url_path.startswith('http://topphimhdz.net'): #layer 2
	if url_path.startswith('http://topphimhd.com/') or url_path.startswith('http://topphimhdz.com') or url_path.startswith('http://topphimhdz.net'): #layer 2
		content = requests.get(url_path, headers=headers2).content
		#item_re = 'episode"><a href="(.*?)"><span>(.*?)</span>'
		item_re = 'episode"><a href="(.*?)"><span.*?">(.*?)</span>'
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, label in matchs:
			thumb = re.findall('movie-thumb" src="(.*?)"', content)[0]
			label = 'Episode - Tập '+label
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	elif url_path.startswith('http://www.hdmoi.net'):
		content = requests.get(url_path, headers=headers2).content
		item_re = 'episode"><a href="(.*?)".*?<span>(.*?)</span>'
		thumb = re.findall('movie-thumb" src="(.*?)"', content)[0]
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, label in matchs:
			label = 'Episode - Tập '+label
			thumb = thumb
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	#elif url_path.startswith('http://www.phumikhmer1'):
	elif 'phumikhmer1' in url_path:
		content = requests.get(url_path, headers=headers2).content
		content = content.replace("'", "\"")
		content = "".join(content.splitlines())
		#item_re = '"file":.*?"(.*?)".*?title":.*?"(.*?)".*?image":.*?"(.*?)"'
		item_re = '"file":.*?"(.*?)".*?title":.*?"(.*?)"'
		matchs = re.compile(item_re).findall(content)
		items = []
		#for path, label, thumb in matchs:
		thumb = 'none'
		for path, label in matchs:
			#if '//ok.ru' in path:
			if path.startswith('//ok.ru'):
				path = path.replace('//ok.ru', 'https://ok.ru')
			if '//www' in path:
				path = path.replace('//www', 'https://www')
			if 'https://youtu.be' in path:
				path = path.replace('https://youtu.be/', 'https://www.youtube.com/watch?v=')+'&feature=youtu.be'
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	#elif url_path.startswith('http://www.khmerdrama') or url_path.startswith('http://www.khmeravenue'):
	elif 'khmerdrama' in url_path or 'khmeravenue' in url_path or 'khmersearch' in url_path: #player2
		content = requests.get(url_path, headers=headers2).content
		content = content.replace("'", "\"")
		#content = "".join(content.splitlines())
		item_re = 'a href="(.*?)".*?btn btn-episode">(.*?)<'
		matchs = re.compile(item_re).findall(content)
		items = []
		thumb = 'none'
		for path, label in matchs:
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	#elif url_path.startswith('http://dl.upload10') or url_path.startswith('http://dl2.upload10'): #from http://builds.kodiuk boxsets
	elif any(url_path.startswith(domain) for domain in ['http://dl.upload10', 'http://dl2.upload10', 'http://dl2.uploadzone', 'http://perserver.ir/', 'https://movies.encrypticmh', \
		'http://rmeyer.comelitdns.com', 'http://103.222.20.150', 'https://tv.encrypticmh.appboxes.co', 'https://franchises.encrypticmh.appboxes.co/', 'http://162.12.215.254']): #Movies 1 Click
		content = requests.get(url_path, headers=headers2).content
		#matchs = re.findall('<a href="(.*?)">(.*?)<',content)[:]
		item_re = '<a href="(.*?)">(.*?)<'
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, label in matchs:
			thumb = ''			
			if '?C=' in path:
				label = 'NONE'
			path = url_path+path
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			if path.endswith('/'):
				item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
			else:
				item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
				item["is_playable"] = True
				item["info"] = {"type": "video"}
			items += [item]
		return items

	elif url_path.startswith('http://ftp.alphamediazone.com'):
		content = requests.get(url_path, headers=headers2).content
		item_re = 'n"><a href="(.*?)">(.*?)<'
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, label in matchs:
			thumb = 'http://mobiletv.mobibase.com/html/logo/hd/channel_ld_434.png'
			path = 'http://ftp.alphamediazone.com'+path
			item = {
				"label": label.strip(),
				"thumbnail": thumb,
				"path": path.strip(),
			}
			if path.endswith('/'):
				item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
			else:
				item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
				item["is_playable"] = True
				item["info"] = {"type": "video"}
			items += [item]	
		return items

	else:
		url = url_path
		return play_url(url)

@plugin.route('/layer2/<path>', name="layer2_default")
@plugin.route('/layer2/<path>/<tracking_string>')
def Layer2(path="0", tracking_string="Layer2"):
	'''
	Liệt kê danh sách các item của sheet layer2 Playlist
	Parameters
	----------
	path : string
		Link chưa nội dung playlist layer2
	tracking_string : string
		 Tên dễ đọc của view
	'''
	GA(  # tracking
		"Layer2 - %s" % tracking_string,
		"/layer2/%s" % path
	)
	#Fix error addtracking playable link
#	if any(words in path for words in ['.mkv', '.mp4', '.avi', '.m3u8', 'https://clipwatching.com', 'https://vidlox.me']): #fix error AddTracking with direct link in layer2
#		items = Layer2ToItems(path)
#		return None
#	else:
#		items = Layer2ToItems(path)
#		return plugin.finish(AddTracking(items))
	items = Layer2ToItems(path)
	return plugin.finish(AddTracking(items))

def M3UToItems(url_path=""):
	'''
	Hàm chuyển đổi m3u playlist sang xbmcswift2 items
	Parameters
	----------
	url_path : string
		link chứa nội dung m3u playlist
	'''
	headers2 = {
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
			'Referer':url_path,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
		}

	if 'swiftstreamz.com' in url_path:
		item_re = 'cat_id":"29",(.*?,)(.*?,)(.*?),"channel_desc'
		(resp, content) = http.request(
			url_path, "GET",
			headers=sheet_headers
		)
		items = []
		matchs = re.compile(item_re).findall(content)
		for label,path,thumb in matchs:
			if "channel_title" in label:
				label = re.compile('channel_title\":\"(.*?)"').findall(label)[0]
			if "channel_url" in path:
				path = re.compile('channel_url\":\"(.*?)"').findall(path)[0]
				linkstream = 'plugin://script.module.streamhublive/play/?url=swift:'+path+'&mode=10&quot'
			if "channel_thumbnail" in thumb:
				thumb = re.compile('channel_thumbnail\":\"(.*?)"').findall(thumb)[0]
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": linkstream.strip(),
			}
			#Xong go to def play_url
			item["path"] = pluginrootpath + \
					"/play/%s" % urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	elif 'https://chaturbate.com' in url_path:
		item_re = 'data-slug=(.*?)><.*?\n<a href=\"(.*?)\".*?\n<img src=\"(.*?)\"'
		(resp, content) = http.request(
			url_path, "GET",
			headers=sheet_headers
		)
		try:
			pages = re.findall('li><a href="(.*?/\?page=.*?)" class="next', content)[0]
			pages = 'https://chaturbate.com'+pages
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'Hết Trang - End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('page=(.*?$)').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for label, path, thumb in matchs:
			label = '[COLOR red][LIVE] [/COLOR][COLOR hotpink]'+label+'[/COLOR]'
			path = 'https://chaturbate.com'+path
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = items + [nextitem]
		return items

	#elif url_path.startswith('http://topphimhd.com') or url_path.startswith('http://topphimhdz.com'):
	elif any(url_path.startswith(domain) for domain in ['http://topphimhd', 'http://topphimhdz.com', 'http://topphimhdz.net']):
	#	if 'xem-phim' in url_path: #layer 2
	#		content = requests.get(url_path, headers=headers2).content
	#		content = "".join(content.splitlines())
	#		#item_re = 'episode"><a href="(.*?)"><span.*?class.*?">(.*?)</span>'
	#		item_re = 'episode"><a href="(.*?)"><span.*?>(.*?)</span>'
	#		#thumb = re.findall('id="expand-post-content".*?src="(.*?)" alt', content)[0]
	#		thumb = re.findall('<p><img class=.*?src="(.*?)"', content)[0]
	#		items = []
	#		items1 =[]
	#		items2 =[]
	#		matchs = re.compile(item_re).findall(content)
	#		if matchs == []: #Incase cannot get path
	#			path = url_path
	#			label = 'Tập - Episode'
	#			thumb = thumb
	#			item = {
	#				"label": label,
	#				"thumbnail": thumb,
	#				"path": path,
	#			}
	#			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
	#			item["is_playable"] = True
	#			item["info"] = {"type": "video"}
	#			items += [item]
	#		for path, label in matchs:
	#			path1 = path
	#			path2 = path.replace('server-1', 'server-2') #server 2
	#			label = 'Tập - Episode '+label
	#			thumb = thumb
	#			item1 = { #server 1
	#				"label": label,
	#				"thumbnail": thumb,
	#				"path": path1,
	#			}
	#			item1["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item1["path"])
	#			item1["is_playable"] = True
	#			item1["info"] = {"type": "video"}
	#			items1 += [item1]
	#			item2 = { #server 2
	#				"label": label,
	#				"thumbnail": thumb,
	#				"path": path2,
	#			}
	#			item2["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item2["path"])
	#			item2["is_playable"] = True
	#			item2["info"] = {"type": "video"}
	#			items2 += [item2]
	#		items = items1+items2
	#		return items

	#	else: #layer 1
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		#item_re = 'class="halim-thumb" href="(.*?)/" title="(.*?)".*?src="(.*?)" alt=".*?title="(.*?)"'
		item_re = 'class="halim-thumb" href="(.*?)/" title="(.*?)".*?src="(.*?)" alt=".*?original_title">(.*?)</p>'
		#item_re = 'a class="halim-thumb" href="(.*?)/" title="(.*?)".*?src="(.*?)" alt=.*?title="(.*?)"'
		try:
			pages = re.findall('next page-numbers" href="(.*?)"><i', content)[0]
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'Hết Trang - End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('page/(.*?)/').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, label1, thumb, label2 in matchs:
			label1 = '[COLOR yellow]'+label1+'[/COLOR]'
			label2 = '[COLOR lime]'+label2+'[/COLOR]'
			label = label1+' - '+label2
			#path = (path.replace('http://topphimhd.com', 'http://topphimhd.com/xem-phim'))+'-tap-1-server-1/'
			path = pluginrootpath+"/layer2/"+urllib.quote_plus(path)
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			items += [item]
		items = items+[nextitem]
		return items

	elif url_path.startswith('https://phimhdonlinetv.com') or url_path.startswith('https://phimhdonlinetv1.com'): #layer 1
		content = requests.get(url_path, headers=headers2).content
		item_re = 'text-center"><a href="(.*?)".*?title="(.*?)".*?src="(.*?)"'
		try:
			pages = re.findall('next page-numbers" href="(.*?)"', content)[0]
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'Hết Trang - End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('page/(.*?)/').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, label, thumb in matchs:
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = items+[nextitem]
		return items

	elif url_path.startswith('http://www.hdmoi.net'):
		content = requests.get(url_path, headers=headers2).content
		#item_re = 'halim-thumb" href="(.*?)".*?(?s)src="(.*?)".*?(?s)episode">(.*?)</.*?(?s)title">(.*?)</.*?title">(.*?)</'
		item_re = 'halim-thumb" href="(.*?)".*?src="(.*?)".*?(?s)<span(.*?)</article>'
		try:
			pages = re.findall('next page-numbers" href="(.*?)"', content)[0]
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'Hết Trang - End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('page/(.*?)/').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		#for path, thumb, label3, label2, label1 in matchs:
		#	label1 = '[COLOR yellow]'+label1+'[/COLOR]'
		#	label2 = '[COLOR lime]'+label2+'[/COLOR]'
		#	label = label1+' - '+label2+' - '+label3
		for path, thumb, info in matchs:
			label1 = ''
			label2 = ''
			label2 = ''
			if 'original_title' in info:
				label1 = re.compile('original_title">(.*?)</').findall(info)[0]
			if 'entry-title' in info:
				label2 = re.compile('entry-title">(.*?)</').findall(info)[0]
			if 'episode' in info:
				label3 = re.compile('episode">(.*?)</').findall(info)[0]
			label = '[COLOR yellow]'+label1+'[/COLOR]'+' - '+'[COLOR lime]'+label2+'[/COLOR]'+' - '+label3
			path = pluginrootpath+"/layer2/"+urllib.quote_plus(path)
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			items += [item]
		items = items+[nextitem]
		return items

	elif url_path.startswith('https://cam2cam.com'):
		item_re = '<img class=\"\" src=\"//(.*?)\".*?alt=\"(.*?)\".*?\n.*?\n.*?\n.*?\n.*?\n.*?href=\"(.*?)\"'
		content = requests.get(url_path, headers=headers2).content
		try:
			pages = 'https://cam2cam.com'+(re.findall('li class=\"active\"><a>.*?\n.*?\n.*?\n.*?<li><a href=\"(.*?)\"', content)[0])
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'Hết Trang - End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('pagenum=(.*?$)').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for thumb, label, path in matchs:
			thumb = 'https://'+thumb
			label = '[COLOR red][LIVE] [/COLOR][COLOR hotpink]'+label+'[/COLOR]'
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = items + [nextitem]
		return items

#	elif url_path.startswith('http://rauma.tv/'):
#		content = requests.get(url_path, headers=headers2).content
#		content = "".join(content.splitlines())
#		item_re = 'matches-lst-tr clearfix.*?href="(.*?)".*?<b>(.*?)</b></p><p>(.*?)</p>' \
#			'.*?<span>(.*?)</span>.*?data-src="(.*?)".*?<span class="">(.*?)</span>.*?</i></span></a>'
#		matchs = re.compile(item_re).findall(content)
#		items = []
#		for path, label1, label4, label2, thumb, label3 in matchs:			
#			label = label1+', '+label2+' vs '+label3+', '+label4
#			if any(words in label for words in ['Hiệp', 'hiệp', 'LIVE']):
#				label1 = '[COLOR lime]'+label1+'[/COLOR]'
#				label2 = '[COLOR yellow]'+label2+'[/COLOR]'
#				label3 = '[COLOR yellow]'+label3+'[/COLOR]'
#				label4 = '[COLOR orange]'+label4+'[/COLOR]'
#				label = label1+', '+label2+' vs '+label3+', '+label4
#			item = {
#				"label": label.strip(),
#				"thumbnail": thumb.strip(),
#				"path": path.strip(),
#			}
#			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
#			item["is_playable"] = True
#			item["info"] = {"type": "video"}
#			items += [item]
#		return items

	elif url_path.startswith('http://keonhacai.net'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = '"match-info well">.*?src="(.*?)".*?h2 class="team">.*?>(.*?)<.*?h2 class="team away">.*?>(.*?)<.*?<span>(.*?)<.*?a href=\'(.*?)\'.*?>(.*?)<'
		matchs = re.compile(item_re).findall(content)
		items = []
		for thumb, label1, label2, label3, path, label4 in matchs:
			label = label1+'vs'+label2+', '+label3+', '+label4
			if 'Đang Xem' in label:
				label1 = '[COLOR lime]'+label1+'[/COLOR]'
				label2 = '[COLOR yellow]'+label2+'[/COLOR]'
				label3 = '[COLOR yellow]'+label3+'[/COLOR]'
				label4 = '[COLOR orange]'+label4+'[/COLOR]'
				label = label1+'vs'+label2+', '+label3+', '+label4
			path = 'http://keonhacai.net/'+path
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	elif url_path.startswith('https://tructiepbongda.vip'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = '<li>.*?<p style=".*?<a href="(.*?)".*?class="match-view">.*?match-status">(.*?)</span>.*?right name-team">' \
			'(.*?)</span>.*?data-src="(.*?)".*?left name-team">(.*?)</span>.*?tour name-comp">(.*?)</span>'
		#item_re = 'list-channel.*?(?s)<a href="/(.*?)".*?class="item.*?(?s)<img src="(.*?)".*?(?s)class="league">(.*?)</div>.*?(?s)class="title">(.*?)</div>.*?(?s)data-time.*?(?s)</span>(.*?)</div>'
		matchs = re.compile(item_re).findall(content)
		notice_time = {
					'label': '------------[COLOR red] Giờ Việt Nam - VietNam Time [/COLOR]------------',
					'thumbnail': 'https://i.imgur.com/KL4qOtF.jpg',
					'path': 'npath'
		}
		items = []
		for path, label1, label2, thumb, label3, label4 in matchs:
			label = label1+', '+label2+' vs '+label3+', '+label4
			if any(words in label for words in ['\'', 'HT']):
				label1 = '[COLOR lime]'+label1+'[/COLOR]'
				label2 = '[COLOR yellow]'+label2+'[/COLOR]'
				label3 = '[COLOR yellow]'+label3+'[/COLOR]'
				label4 = '[COLOR orange]'+label4+'[/COLOR]'
				label = label1+', '+label2+' vs '+label3+', '+label4
			path = 'https://tructiepbongda.vip'+path
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = [notice_time]+items
		return items

	elif url_path.startswith('https://live.90phut.tv') or url_path.startswith('https://live1.90p.tv'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = 'list-channel.*?<a href="/(.*?)".*?class="item.*?<img src="(.*?)".*?class="league">' \
			'(.*?)</div>.*?class="title">(.*?)</div>.*?data-time.*?</span>(.*?)</div>'
		matchs = re.compile(item_re).findall(content)
		source_t = requests.get('https://www.timeanddate.com/worldclock/fullscreen.html?n=95', headers=headers2).text
		try:
			label_t = re.findall('<div id=i_time>(.*?)</div>', source_t)[0]
		except:
			label_t = ''
		notice_time = {
					'label': '------------ '+'[COLOR lime]'+label_t+'[/COLOR]'+'[COLOR red] Giờ Việt Nam - VietNam Time [/COLOR]------------',
					#'thumbnail': 'https://i.imgur.com/KL4qOtF.jpg',
					'thumbnail': 'https://c.tadst.com/gfx/citymap/vn-10.png?10',
					'path': 'None'
		}
		items = []
		for path, thumb, label3, label2, label1 in matchs:
			#label1 = '[COLOR lime]'+label1+'[/COLOR]'
			label1 = label1.strip()
			#label2 = '[COLOR yellow]'+label2+'[/COLOR]'
			label2 = label2.strip()
			#label3 = '[COLOR orange]'+label3+'[/COLOR]'
			label3 = label3.strip()
			label = label1+', '+label2+', '+label3
			path = 'https://live1.90p.tv/'+path
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = [notice_time]+items
		return items

#	elif url_path.startswith('https://www.film2movie.ws'):
#		content = requests.get(url_path, headers=headers2).content
#		content = "".join(content.splitlines())
#		item_re = '<article class.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"'
#		try:
#			pages = re.findall('class=\'textwpnumb\'.*?href=\'(.*?)\'', content)[0]
#		except:
#			pages = 'none'
#		if pages == 'none':
#			nlabel = 'Hết Trang - End of Pages'
#		else:
#			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('page/(.*?)/').findall(pages)[0]
#		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
#		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
#		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
#		matchs = re.compile(item_re).findall(content)
#		items = []
#		for path, label, thumb in matchs:
#			label = re.findall(r'[0-z]+', label) #Alphabet & number only, no arabic
#			label = '[COLOR orange]'+" ".join(label)+'[/COLOR]'
#			item = {
#				"label": label.strip(),
#				"thumbnail": thumb.strip(),
#				"path": path.strip(),
#			}
#			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
#			item["is_playable"] = True
#			item["info"] = {"type": "video"}
#			items += [item]
#		items = items + [nextitem]
#		return items

	elif url_path.startswith('https://bilutvz.com') or url_path.startswith('https://bilumoi.com') or url_path.startswith('https://zingtvz.org'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = 'current-status">(.*?)<.*?href="(.*?)".*?src="(.*?)".*?class=.*?name">(.*?)</p>.*?real-name">(.*?)<'
		try:
			pages = re.findall('pagination">.*?current" href=.*?href="(.*?)"', content)[0]
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'Hết Trang - End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('trang-(.*?)\.html').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for label3, path, thumb, label2, label1 in matchs:
			label = '[COLOR lime]'+label1+'[/COLOR]'+'-'+'[COLOR yellow]'+label2+'[/COLOR]'+'-'+label3
			#thumb = 'http://'+thumb
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
			items += [item]
		items = items + [nextitem]
		return items

	elif url_path.startswith('http://www.phumikhmer1'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = "<article class=.*?<link href='(.*?)'.*?<div class='post-summary'.*?<meta content=\'(.*?)' itemprop='url'/>.*?title='(.*?)'"
		try:
			page_num = re.findall('PageNo=(.*?$)', url_path)[0]
		except:
			page_num = '1'
		page_num = int(page_num)+1
		page_num = str(page_num)
		try:
			pages = re.findall("blog-pager-older-link btn' href='(.*?)&start", content)[0]
			pages = pages+'#PageNo='+page_num
		except:
			try:
				pages = re.findall("blog-pager-older-link btn' href='(.*?)'", content)[0]
				pages = pages+'#PageNo='+page_num
			except:
				pages = 'none'
		if pages == 'none':
			nlabel = 'End of Pages'
		else:
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+page_num
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, thumb, label in matchs:
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
			items += [item]
		items = items + [nextitem]
		return items

	elif url_path.startswith('http://www.khmerdrama') or url_path.startswith('http://www.khmeravenue'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = 'thumbnail-container.*?href="(.*?)".*?image: url\((.*?)\).*?<h4> (.*?)</h4>.*?<h3>(.*?)</h3>'
		try:
			pages = re.findall('page larger" title="Page.*?href="(.*?)"', content)[0]
		except:
			pages = 'none'
		if pages == 'none':
			nlabel = 'End of Pages'
		else:		
			nlabel = '[COLOR yellow]Next Page>>[/COLOR]'+re.compile('page/(.*?)/').findall(pages)[0]
		nthumb = 'https://cdn.pixabay.com/photo/2017/06/20/14/55/icon-2423349_960_720.png'
		npath = pluginrootpath+"/m3u/"+urllib.quote_plus(pages)
		nextitem = {'label': nlabel, 'thumbnail': nthumb, 'path': npath}
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, thumb, label2, label1 in matchs:
			label = '[COLOR lime]'+label1+'[/COLOR]'+', '+label2
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
			items += [item]
		items = items + [nextitem]
		return items

	#elif any(url_path.startswith(domain) for domain in ['http://worldkodi.com', 'http://colussus.net/', 'http://builds.kodiuk.tv']):
	elif url_path.endswith('.xml') or url_path.endswith('linkxml'):
		url = url_path.replace('/linkxml', '')
		content = requests.get(url_path, headers=headers2).content
		if '<item>' in content:
			#content = "".join(content.splitlines())
			#item_re = '.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<thumbnail>(.*?)</thu.*?nail>'
			#matchs = re.compile(item_re).findall(content)
			#matchs = re.findall('<item>.+?(?s)<title>([^\</]+).+?(?s)<link>(?s)(.*?)</lin.+?(?s)<thumbnail>(.*?)</thumb',content)[:] #(.?)included lines, ([])special char
			matchs = re.findall('<item>.+?(?s)<title>(.*?)</t.+?(?s)<link>(?s)(.*?)</lin.+?(?s)<thumbnail>(.*?)</thumb',content)[:]
			items = []
			for label, path, thumb in matchs:
				item = {
					"label": label.strip(),
					"thumbnail": thumb.strip(),
 					"path": path.strip(),
				}
				if '<sublink>' in item["path"]:
					#item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
					item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
				else: #Playabel link
					item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
				item["is_playable"] = True
				item["info"] = {"type": "video"}
				items += [item]
			return items
		if '<dir>' in content or '<plugin>' in content:
		#if '<dir>' in content:
			matchs = re.findall('<title>([^</]+).+?(?s)<link>(?s)(.*?)</lin.+?(?s)<thumbnail>(.*?)</thumb',content)[:] #(.?)included lines, ([])special char
			items = []
			for label, path, thumb in matchs:
				item = {
					"label": label.strip(),
					"thumbnail": thumb.strip(),
 					"path": path.strip(),
				}
				#if item["path"].startswith('http://dl.upload10'):
				if any(item["path"].startswith(domain) for domain in ['http://dl.upload10', 'http://dl2.upload10', 'http://dl2.uploadzone']):
					item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
				elif item["path"].startswith('<sublink>'):
					#item["path"] = pluginrootpath + "/layer2/" + urllib.quote_plus(item["path"])
					item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
				else:
					item["path"] = pluginrootpath + "/m3u/" + urllib.quote_plus(item["path"])
				items += [item]
			return items

#	elif url_path.startswith('http://60fps'):
#		content = requests.get(url_path, headers=headers2).content
#		item_re = '<p style=.*?title=.*?href="(.*?)">(.*?)<'
#		matchs = re.compile(item_re).findall(content)
#		items = []
#		for path, label in matchs:
#			thumb = 'none'
#			label = '[COLOR yellow]'+label+'[/COLOR]'
#			item = {
#				"label": label.strip(),
#				"thumbnail": thumb.strip(),
#				"path": path.strip(),
#			}
#			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
#			item["is_playable"] = True
#			item["info"] = {"type": "video"}
#			items += [item]
#		return items

	elif url_path.startswith('http://60fps'):
		content = requests.get(url_path, headers=headers2).content
		item_re = '<p style=(.*?)</p>'
		matchs = re.compile(item_re).findall(content)
		items = []
		for info in matchs:
			thumb = ''
			if 'href' in info:
				path = re.compile('href="(.*?)"').findall(info)[0]
			else:
				path = ''
			if 'vs <a title="' in info:
				label1 = re.compile('title="(.*?)"').findall(info)[0]
				try:
					label2 = re.compile('title=".*?title="(.*?)"').findall(info)[0]
				except:
					try:
						label2 = re.compile(';">(.*?) vs <a title=').findall(info)[0]
					except:
						label2 = ''
				label = '[COLOR yellow]'+label1+'[/COLOR]'+' vs '+'[COLOR yellow]'+label2+'[/COLOR]'
			elif 'title' in info:
				label = re.compile('title="(.*?)"').findall(info)[0]
				label = '[COLOR orange]'+label+'[/COLOR]'
			elif 'img' in info or 'input' in info:
				label = 'NONE'
			else:
				label = 'Not Start Yet'
				label = '[COLOR lime]'+label+'[/COLOR]'
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	#elif url_path.startswith('http://crackstreams.com') or url_path.startswith('http://nbastreams.xyz') or ('http://crackstreams.is'):
	elif url_path.startswith('http://live13.crackstreams.net') or url_path.startswith('http://crackstreams.net') or url_path.startswith('http://hd.crackstreams.net') or url_path.startswith('http://new.crackstreams.net') or url_path.startswith('http://ww3.crackstreams.net'):
		content = requests.get(url_path, headers=headers2).content
		#content = "".join(content.splitlines())
		#item_re = "<a href='(.*?)'.*?<img src='(.*?)'.*?media-heading'>(.*?)<.*?<p>(.*?)</p>"
		item_re = "<a href='(.*?)'.*?(?s)<img src='(.*?)'.*?(?s)<h4 class=(.*?)</div>"
		matchs = re.compile(item_re).findall(content)
		source_t = requests.get('https://www.timeanddate.com/worldclock/fullscreen.html?n=77', headers=headers2).text
		try:
			label_t = re.findall('<div id=i_time>(.*?)</div>', source_t)[0]
		except:
			label_t = ''
		notice_time = {
					'label': '------------ '+'[COLOR lime]'+label_t+'[/COLOR]'+'[COLOR red] Giờ Eastern - Eastern Time [/COLOR]------------',
					'thumbnail': 'https://c.tadst.com/gfx/tzpage/est.1572778800.png?1292',
					'path': 'None'
		}
		items = []
		for path, thumb, info in matchs:
			label1 = ''
			label2 = ''
			thumb = 'http://live13.crackstreams.net'+thumb
			if path.startswith('/'):
				path = 'http://live13.crackstreams.net'+path
			if path.startswith('http'):
				path = path
			else:
				path = 'http://live13.crackstreams.net/'+path
			if 'media-heading' in info:
				#label1 = re.compile("media-heading'>(.*?)</").findall(info)[0]
				label1 = re.compile("media-heading>|media-heading'>(.*?)</").findall(info)[0]
			if '<p>' in info:
				label2 = re.compile("<p>(.*?)</").findall(info)[0]
			label = '[COLOR lime]'+label2+'[/COLOR]'+', '+'[COLOR yellow]'+label1+'[/COLOR]'
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = [notice_time]+items
		return items

	elif url_path.startswith('http://nbastreams.site'):
		content = requests.get(url_path, headers=headers2).content
		#content = "".join(content.splitlines())
		#item_re = "<a href='(.*?)'.*?<img src='(.*?)'.*?media-heading'>(.*?)<.*?<p>(.*?)</p>"
		item_re = "<a href='(.*?)'.*?(?s)<h4 class=(.*?)(?s)</div>"
		matchs = re.compile(item_re).findall(content)
		source_t = requests.get('https://www.timeanddate.com/worldclock/fullscreen.html?n=77', headers=headers2).text
		try:
			label_t = re.findall('<div id=i_time>(.*?)</div>', source_t)[0]
		except:
			label_t = ''
		notice_time = {
					'label': '------------ '+'[COLOR lime]'+label_t+'[/COLOR]'+'[COLOR red] Giờ Eastern - Eastern Time [/COLOR]------------',
					'thumbnail': 'https://c.tadst.com/gfx/tzpage/est.1572778800.png?1292',
					'path': 'None'
		}
		items = []
		for path, info in matchs:
			label1 = ''
			label2 = ''
			thumb = ''
			if path.startswith('/'):
				path = 'http://nbastreams.site'+path
			if 'media-heading' in info:
				label1 = re.compile("media-heading'>(.*?)</").findall(info)[0]
				#label1 = re.compile("media-heading>|media-heading'>(.*?)</").findall(info)[0]
			if '<p>' in info:
				label2 = re.compile("<p>(.*?)</").findall(info)[0]
			label = '[COLOR lime]'+label2+'[/COLOR]'+', '+'[COLOR yellow]'+label1+'[/COLOR]'
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = [notice_time]+items
		return items

	elif url_path.startswith('http://6stream.xyz') or url_path.startswith('http://6streams.tv'):
		content = requests.get(url_path, headers=headers2).content
		item_re = '<figure class=".*?data-original="(.*?)".*?href="(.*?)".*?title="(.*?)".*?(?s)datePublished">(.*?)<'
		matchs = re.compile(item_re).findall(content)
		items = []
		for thumb, path, label1, label2 in matchs:
			label = '[COLOR lime]'+label1+'[/COLOR]'+', '+'[COLOR yellow]'+label2+'[/COLOR]'
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	elif url_path.startswith('https://daddylive.live') or url_path.startswith('https://daddylive.club'):
		url1='https://daddylive.live/'
		#sport_name=re.findall('/(\w+)$', url_path)[0]
		sport_name=re.findall('daddylive.live/(.*?)$', url_path)[0]
		content = requests.get(url1, headers=headers2).content
		#matchs = re.findall('(<p>.*?|<br />.*?)<a href="(.*?)".*?;">(.*?)</', re.findall('%s</span>(.*?)(?s)</a></p>' % sport_name, content)[0])
		#match = re.findall('>%s</span>(.*?)(?s)</a></p>' % sport_name, content)
		#match = re.findall('>%s</span>(.*?)(?s)<p>==' % sport_name, content)
		#match = re.findall('>%s</span>(.*?)(?s)</span></a></p>' % sport_name, content)
		#match = re.findall('>%s</span>(.*?)(?s)</span></strong></a></p>' % sport_name, content)
		#match = re.findall('>%s</span>(.*?)(?s)</span></a></p>' % sport_name, content)
		match = re.findall('>%s</span>(.*?)(?s)</span></a></p>|</span></strong></a></p>' % sport_name , content)
		matchs = []
		for n in range(len(match)):
			#match2 = re.findall('(<p>.*?|<br />.*?)<a href="(.*?)".*?;">(.*?)</', match[n])
			match2 = re.findall(';">(.*?)<a href="(.*?)".*?;">(.*?)</', match[n])
			matchs += match2

		source_t = requests.get('https://www.timeanddate.com/worldclock/fullscreen.html?n=69', headers=headers2).text
		try:
			#####Change to 24H####
			time = re.findall('<div id=i_time>(.*?)</div>', source_t)[0]
			time_r = time.replace('am', '')
			time_r = time_r.replace('pm', '')
			h_st = re.findall('(^.*?):', time)[0]
			h_in = int(h_st)
			if 'pm' in time:
				time_h = h_in+12
				time_h = str(time_h)
				time_ch = time_r.replace(h_st, time_h)
				if '12' in h_st:
					time_ch = time_r
			else:
				time_ch = time_r
			###### End ######
		except:
			time_ch = ''
		notice_time = {
					'label': '------------ '+'[COLOR lime]'+time_ch+'[/COLOR]'+'[COLOR red] Giờ UK GMT+1 - UK GMT+1 Time [/COLOR]------------',
					'thumbnail': 'https://c.tadst.com/gfx/tzpage/cet.1573308000.png?1292',
					'path': 'None'
		}
		items = []
		for label1, path, label2 in matchs:
			#label1 = ''
			thumb = 'https://t3.ftcdn.net/jpg/00/17/46/90/240_F_17469077_tbWv6MUkv0wMWdZNO7uZnf8QUFCVjtoS.jpg'
			#if '<p>' or '<br />' in label1:
			#if '</span>' or '</strong>' or '</a>' in label1:
			if any(words in label1 for words in ['</span>', '</strong>', '</a>', '<br />', '<span style="color: #0000ff;">']):
				#label1 = label1.replace('<p>', '')
				#label1 = label1.replace('<br />', '')
				label1 = label1.replace('</span>', '').replace('</strong>', '').replace('</a>', '').replace('<br />', '').replace('<span style="color: #0000ff;">', '')
			label = '[COLOR lime]'+label1+'[/COLOR]'+', '+'[COLOR yellow]'+label2+'[/COLOR]'
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		items = [notice_time]+items
		return items

	elif url_path.startswith('https://ok.ru'):
		content = requests.get(url_path, headers=headers2).content
		content = "".join(content.splitlines())
		item_re = 'card_img-w"><a href="(.*?)".*?<img onerror=.*?src="(.*?)".*?title="(.*?)"'
		matchs = re.compile(item_re).findall(content)
		items = []
		for path, thumb, label in matchs:
			path = 'https://ok.ru'+path
			#thumb = 'https:'+thumb
			thumb = thumb.replace('&amp;', '&')
			item = {
				"label": label.strip(),
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}
			item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			item["is_playable"] = True
			item["info"] = {"type": "video"}
			items += [item]
		return items

	else:
		item_re = '\#EXTINF(.*?,)(.*?)\n(.*?)\n'
		(resp, content) = http.request(
			url_path, "GET",
			headers=sheet_headers
		)
		items = []
		matchs = re.compile(item_re).findall(content)
		for info, label, path in matchs:
			thumb = ""
			label2 = ""
			if "tvg-logo" in info:
				#thumb = re.compile('tvg-logo=\"?(.*?)\"?,').findall(info)[0]
				thumb = re.compile('tvg-logo="(.*?)"').findall(info)[0]
			if "group-title" in info:
				label2 = re.compile('group-title="(.*?)"').findall(info)[0]
			if label2 != "":
				label2 = "[%s] " % label2.strip()
			label = "%s%s" % (label2, label.strip())
			item = {
				"label": label,
				"thumbnail": thumb.strip(),
				"path": path.strip(),
			}

			# Nếu là playable link
			if "://" in item["path"]:
				# Kiểu link plugin://
				if item["path"].startswith("plugin://"):
					item["is_playable"] = True
					item["info"] = {"type": "video"}
				# Kiểu link .ts
				elif re.search("\.ts$", item["path"]):
					item["path"] = "plugin://plugin.video.f4mTester/?url=%s&streamtype=TSDOWNLOADER&use_proxy_for_chunks=True&name=%s" % (
						urllib.quote(item["path"]),
						urllib.quote_plus(item["label"])
					)
					item["path"] = pluginrootpath + \
						"/executebuiltin/" + urllib.quote_plus(item["path"])
				# Kiểu direct link
				else:
					if "acestream" in item["path"]:
						item["label"] = "[AceStream] %s" % item["label"]
					item["path"] = pluginrootpath + \
						"/play/%s" % urllib.quote_plus(item["path"])
					item["is_playable"] = True
					item["info"] = {"type": "video"}
			else:
				# Nếu không phải...
				item["is_playable"] = False

			# Hack xbmcswift2 item to set both is_playable and is_folder to False
			# Required for f4mTester
			if "f4mTester" in item["path"]:
				item["is_playable"] = False
			items += [item]
		return items


@plugin.cached(ttl=525600)
def getCachedItems(url_path="0"):
	return AddTracking(getItems(url_path))


def getItems(url_path="0", tq="select A,B,C,D,E"):
	'''
	Tạo items theo chuẩn xbmcswift2 từ Google Spreadsheet
	Parameters
	----------
	url_path : string
		Nếu truyền "gid" của Repositories sheet:
			Cài tự động toàn bộ repo trong Repositories sheet
		Nếu truyền link download zip repo
			Download và cài zip repo đó
	tracking_string : string
		 Tên dễ đọc của view
	'''
	# Default VN Open Playlist Sheet ID

	sheet_id = GetSheetIDFromSettings()
	gid = url_path
	if "@" in url_path:
		path_split = url_path.split("@")
		gid = path_split[0]
		sheet_id = path_split[1]
	history = plugin.get_storage('history')
	if "sources" in history:
		history["sources"] = ["https://docs.google.com/spreadsheets/d/%s/edit#gid=%s" %
                        (sheet_id, gid)] + history["sources"]
		history["sources"] = history["sources"][0:4]
	else:
		history["sources"] = [
			"https://docs.google.com/spreadsheets/d/%s/edit#gid=%s" % (sheet_id, gid)]
	url = query_url.format(
		sid=sheet_id,
		tq=urllib.quote(tq),
		gid=gid
	)
	(resp, content) = http.request(
		url, "GET",
		headers=sheet_headers
	)
	_re = "google.visualization.Query.setResponse\((.+)\);"
	_json = json.loads(re.compile(_re).findall(content)[0])
	items = []
	for row in _json["table"]["rows"]:
		item = {}
		item["label"] = getValue(row["c"][0]).encode("utf-8")
		item["label2"] = getValue(row["c"][4])
		# Nếu phát hiện spreadsheet khác với VNOpenPlaylist
		new_path = getValue(row["c"][1])
		if "@" in url_path and "@" not in new_path and "section/" in new_path:
			gid = re.compile("section/(\d+)").findall(new_path)[0]
			new_path = re.sub(
				'section/\d+',
				'section/%s@%s' % (gid, sheet_id),
				new_path,
				flags=re.IGNORECASE
			)
		item["path"] = new_path

		item["thumbnail"] = getValue(row["c"][2])
		item["info"] = {"plot": getValue(row["c"][3])}
		if "plugin://" in item["path"]:
			if "install-repo" in item["path"]:
				item["is_playable"] = False
			elif re.search("plugin.video.vinh.movies/(.+?)/.+?\://", item["path"]):
				match = re.search(
					"plugin.video.vinh.movies(/.+?/).+?\://", item["path"])
				tmp = item["path"].split(match.group(1))
				tmp[-1] = urllib.quote_plus(tmp[-1])
				item["path"] = match.group(1).join(tmp)
				if "/play/" in match.group(1):
					item["is_playable"] = True
					item["info"] = {"type": "video"}
			elif item["path"].startswith("plugin://plugin.video.f4mTester"):
				item["is_playable"] = False
				item["path"] = pluginrootpath + \
					"/executebuiltin/" + urllib.quote_plus(item["path"])
			elif "/play/" in item["path"]:
				item["is_playable"] = True
				item["info"] = {"type": "video"}
		elif item["path"] == "":
			item["label"] = "[I]%s[/I]" % item["label"]
			item["is_playable"] = False
			item["path"] = pluginrootpath + "/executebuiltin/-"
		else:
			if "spreadsheets/d/" in item["path"]:
				# https://docs.google.com/spreadsheets/d/1zL6Kw4ZGoNcIuW9TAlHWZrNIJbDU5xHTtz-o8vpoJss/edit#gid=0
				match_cache = re.search('cache=(.+?)($|&)', item["path"])
				match_passw = re.search('passw=(.+?)($|&)', item["path"])

				sheet_id = re.compile("/d/(.+?)/").findall(item["path"])[0]
				try:
					gid = re.compile("gid=(\d+)").findall(item["path"])[0]
				except:
					gid = "0"
				item["path"] = pluginrootpath + "/section/%s@%s" % (gid, sheet_id)
				if match_cache:
					cache_version = match_cache.group(1)
					item["path"] = pluginrootpath + \
						"/cached-section/%s@%s@%s" % (gid, sheet_id, cache_version)
				elif match_passw:
					item["path"] = pluginrootpath + \
						"/password-section/%s/%s@%s" % (match_passw.group(1), gid, sheet_id)
			elif re.search(r'textuploader', item["path"]):
				item["path"] = pluginrootpath + \
					"/m3u/" + urllib.quote_plus(item["path"])
			elif any(service in item["path"] for service in ["acelisting.in"]):
				item["path"] = pluginrootpath + \
					"/acelist/" + urllib.quote_plus(item["path"])
			elif any(service in item["path"] for service in ["fshare.vn/folder"]):
				item["path"] = pluginrootpath + "/fshare/" + \
					urllib.quote_plus(item["path"].encode("utf8"))
				# item["path"] = "plugin://plugin.video.xshare/?mode=90&page=0&url=" + urllib.quote_plus(item["path"])
			elif any(service in item["path"] for service in ["4share.vn/d/"]):
				item["path"] = "plugin://plugin.video.xshare/?mode=38&page=0&url=" + \
					urllib.quote_plus(item["path"])
			elif any(service in item["path"] for service in ["4share.vn/f/"]):
				# elif any(service in item["path"] for service in ["4share.vn/f/", "fshare.vn/file"]):
				item["path"] = "plugin://plugin.video.xshare/?mode=3&page=0&url=" + \
					urllib.quote_plus(item["path"])
				item["is_playable"] = True
				item["info"] = {"type": "video"}
				item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
			elif "youtube.com/channel" in item["path"]:
				# https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ
				yt_route = "ytcp" if "playlists" in item["path"] else "ytc"
				yt_cid = re.compile("youtube.com/channel/(.+?)$").findall(item["path"])[0]
				item["path"] = "plugin://plugin.video.kodi4vn.launcher/%s/%s/" % (
					yt_route, yt_cid)
				item["path"] = item["path"].replace("/playlists", "")
			elif "youtube.com/playlist" in item["path"]:
				# https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI
				yt_pid = re.compile("list=(.+?)$").findall(item["path"])[0]
				item["path"] = "plugin://plugin.video.kodi4vn.launcher/ytp/%s/" % yt_pid
			elif any(ext in item["path"] for ext in [".png", ".jpg", ".bmp", ".jpeg"]):
				item["path"] = "plugin://plugin.video.kodi4vn.launcher/showimage/%s/" % urllib.quote_plus(
					item["path"])
			elif re.search("\.ts$", item["path"]):
				item["path"] = "plugin://plugin.video.f4mTester/?url=%s&streamtype=TSDOWNLOADER&use_proxy_for_chunks=True&name=%s" % (
					urllib.quote(item["path"]),
					urllib.quote_plus(item["label"])
				)
				item["path"] = pluginrootpath + \
					"/executebuiltin/" + urllib.quote_plus(item["path"])
			else:
				# Nếu là direct link thì route đến hàm play_url
				item["is_playable"] = True
				item["info"] = {"type": "video"}
				item["path"] = pluginrootpath + "/play/" + urllib.quote_plus(item["path"])
		if item["label2"].startswith("http"):
			item["path"] += "?sub=" + urllib.quote_plus(item["label2"].encode("utf8"))
		items += [item]
	if url_path == "0":
		add_playlist_item = {
			"context_menu": [
				ClearPlaylists(""),
			],
			"label": "[COLOR yellow]*** Thêm Playlist ***[/COLOR]",
			"path": "%s/add-playlist" % (pluginrootpath),
			"thumbnail": "http://1.bp.blogspot.com/-gc1x9VtxIg0/VbggLVxszWI/AAAAAAAAANo/Msz5Wu0wN4E/s1600/playlist-advertorial.png",
			"is_playable": True,
			"info": {"type": "video"}

		}
		items += [add_playlist_item]
		playlists = plugin.get_storage('playlists')
		if 'sections' in playlists:
			for section in playlists['sections']:
				item = {
					"context_menu": [
						ClearPlaylists(section),
					]
				}
				if "@@" in section:
					tmp = section.split("@@")
					passw = tmp[-1]
					section = tmp[0]
					item["label"] = section
					item["path"] = "%s/password-section/%s/%s" % (
						pluginrootpath,
						passw,
						section.split("] ")[-1]
					)
				else:
					item["label"] = section
					item["path"] = "%s/section/%s" % (
						pluginrootpath,
						section.split("] ")[-1]
					)
				item["thumbnail"] = "http://1.bp.blogspot.com/-gc1x9VtxIg0/VbggLVxszWI/AAAAAAAAANo/Msz5Wu0wN4E/s1600/playlist-advertorial.png"
				items.append(item)
	return items


@plugin.route('/remove-playlists/', name="remove_all")
@plugin.route('/remove-playlists/<item>')
def RemovePlaylists(item=""):
	item = urllib.unquote_plus(item)
	if item is not "":
		playlists = plugin.get_storage('playlists')
		if 'sections' in playlists:
			new_playlists = []
			for section in playlists["sections"]:
				if section != item:
					new_playlists += [section]
			playlists["sections"] = new_playlists
	else:
		plugin.get_storage('playlists').clear()
	xbmc.executebuiltin('Container.Refresh')


def ClearPlaylists(item=""):
	if item == "":
		label = '[COLOR yellow]Xóa hết Playlists[/COLOR]'
	else:
		label = '[COLOR yellow]Xóa "%s"[/COLOR]' % item

	return (label, actions.background(
		"%s/remove-playlists/%s" % (pluginrootpath, urllib.quote_plus(item))
	))


def getValue(colid):
	'''
	Hàm lấy giá trị theo cột của của mỗi dòng sheet
	Parameters
	----------
	colid : string
		Số thự tự của cột
	'''
	if colid is not None and colid["v"] is not None:
		return colid["v"]
	else:
		return ""


@plugin.route('/')
def Home():
	'''	Main Menu
	'''
	GA()  # tracking
	Section("0")


@plugin.route('/cached-section/<path>/<tracking_string>')
def CachedSection(path="0", tracking_string="Home"):
	GA(  # tracking
		"Section - %s" % tracking_string,
		"/section/%s" % path
	)
	return plugin.finish(getCachedItems(path))


@plugin.route('/password-section/<password>/<path>/<tracking_string>')
def PasswordSection(password="0000", path="0", tracking_string="Home"):
	'''
	Liệt kê danh sách các item của một sheet
	Parameters
	----------
	path : string
		"gid" của sheet
	tracking_string : string
		 Tên dễ đọc của view
	'''
	GA(  # tracking
		"Password Section - %s" % tracking_string,
		"/password-section/%s" % path
	)
	passwords = plugin.get_storage('passwords')
	if password in passwords and (time.time() - passwords[password] < 1800):
		items = AddTracking(getItems(path))
		return plugin.finish(items)
	else:
		passw_string = plugin.keyboard(heading='Nhập password')
		if passw_string == password:
			passwords[password] = time.time()
			items = AddTracking(getItems(path))
			return plugin.finish(items)
		else:
			header = "Sai mật khẩu!!!"
			message = "Mật khẩu không khớp. Không tải được nội dung"
			xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' %
			                    (header, message, 10000, ''))
			return plugin.finish()


@plugin.route('/section/<path>/<tracking_string>')
def Section(path="0", tracking_string="Home"):
	'''
	Liệt kê danh sách các item của một sheet
	Parameters
	----------
	path : string
		"gid" của sheet
	tracking_string : string
		 Tên dễ đọc của view
	'''
	GA(  # tracking
		"Section - %s" % tracking_string,
		"/section/%s" % path
	)
	items = AddTracking(getItems(path))
	return plugin.finish(items)


@plugin.route('/add-playlist/<tracking_string>')
def AddPlaylist(tracking_string="Add Playlist"):
	sheet_url = plugin.keyboard(
		heading='Nhập URL của Google Spreadsheet (có hỗ trợ link rút gọn như bit.ly, goo.gl)')
	if sheet_url:
		if not re.match("^https*://", sheet_url):
			sheet_url = "https://" + sheet_url
		try:
			resp, content = http.request(sheet_url, "HEAD")
			sid, gid = re.compile(
				"/d/(.+?)/.+?gid=(\d+)").findall(resp["content-location"])[0]
			match_passw = re.search('passw=(.+?)($|&)', resp["content-location"])
			playlists = plugin.get_storage('playlists')
			name = plugin.keyboard(heading='Đặt tên cho Playlist')

			item = "[[COLOR yellow]%s[/COLOR]] %s@%s" % (name, gid, sid)
			if match_passw:
				item += "@@" + match_passw.group(1)
			if 'sections' in playlists:
				playlists["sections"] = [item] + playlists["sections"]
			else:
				playlists["sections"] = [item]
			xbmc.executebuiltin('Container.Refresh')
		except:
			line1 = "Vui lòng nhập URL hợp lệ. Ví dụ dạng đầy đủ:"
			line2 = "http://docs.google.com/spreadsheets/d/xxx/edit#gid=###"
			line3 = "Hoặc rút gọn: http://bit.ly/xxxxxx hoặc http://goo.gl/xxxxx"
			dlg = xbmcgui.Dialog()
			dlg.ok("URL không hợp lệ!!!", line1, line2, line3)


@plugin.route('/acelist/<path>/<tracking_string>')
def AceList(path="0", tracking_string="AceList"):
	(resp, content) = http.request(
		path, "GET",
		headers=sheet_headers
	)
	items = []
	match = re.compile('<td class="text-right">(.+?)</td></tr><tr><td class="xsmall text-muted">(.+?)</td></tr></table></td><td>(.+?)</td>.+?href="(acestream.+?)".+?title = "(.+?)"').findall(cleanHTML(content))
	for _time, _date, sport, aceurl, title in match:
		titles = title.strip().split("<br />")
		titles[0] = "[COLOR yellow]%s[/COLOR]" % titles[0]
		title = " - ".join(titles)
		title = "[B][COLOR orange]%s, %s[/COLOR] %s %s[/B]" % (
			_date.strip(), re.sub('<.*?>', '', _time).strip(), sport.strip(), title)
		item = {}
		item["label"] = title
		item["path"] = "%s/play/%s/%s" % (
			pluginrootpath,
			urllib.quote_plus(aceurl),
			urllib.quote_plus("[AceList] %s" % item["label"])
		)
		item["is_playable"] = True
		item["info"] = {"type": "video"}
		items += [item]
	return plugin.finish(items)


@plugin.route('/fshare/<path>/<tracking_string>')
def FShare(path="0", tracking_string="FShare"):
	def toSize(s):
		gb = 2**30
		mb = 2**20
		try:
			s = int(s)
		except:
			s = 0
		if s > gb:
			s = '{:.2f} GB'.format(s/gb)
		elif s > mb:
			s = '{:.0f} MB'.format(s/mb)
		else:
			s = '{:.2f} MB'.format(s/mb)
		return s
	folder_id = re.search('folder/(.+?)(\?|$)', path).group(1)
	page = 1
	try:
		page = int(re.search('page=(\d+)', path).group(1))
	except:
		pass
	fshare_folder_api = "https://www.fshare.vn/api/v3/files/folder?linkcode=%s&sort=type,-modified&page=%s" % (
		folder_id, page)
	(resp, content) = http.request(
		fshare_folder_api, "GET",
		headers={
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Encoding": "gzip, deflate, sdch, br"
		}
	)
	items = []
	fshare_items = json.loads(content)["items"]
	for i in fshare_items:
		item = {}
		name = i["name"].encode("utf8")
		size = 0
		try:
			size = toSize(i["size"])
		except:
			pass

		if not i["type"]:  # is folder
			item["path"] = "%s/fshare/%s/%s" % (
				pluginrootpath,
				urllib.quote_plus("https://www.fshare.vn/folder/" + i["linkcode"]),
				urllib.quote_plus("[FShare] %s" % name)
			)
			item["label"] = "[FShare] %s" % name
		else:
			item["path"] = "%s/play/%s/%s" % (
				pluginrootpath,
				urllib.quote_plus("https://www.fshare.vn/file/" + i["linkcode"]),
				urllib.quote_plus("[FShare] %s (%s)" % (name, size))
			)
			item["label"] = "%s (%s)" % (name, size)
			item["is_playable"] = True
			item["info"] = {"type": "video"}
		items += [item]
	if len(fshare_items) >= 20:
		path = "https://www.fshare.vn/folder/%s?page=%s" % (folder_id, page + 1)
		items.append({
			'label': 'Next >>',
			'path': '%s/fshare/%s/%s' % (
				pluginrootpath,
				urllib.quote_plus(path),
				urllib.quote_plus(tracking_string)
			),
			'thumbnail': "https://docs.google.com/drawings/d/12OjbFr3Z5TCi1WREwTWECxNNwx0Kx-FTrCLOigrpqG4/pub?w=256&h=256"
		})
	return plugin.finish(items)


@plugin.route('/m3u-section/<path>/<tracking_string>')
def M3USection(path="0", tracking_string="M3U"):
	'''
	Liệt kê danh sách các item của sheet M3U Playlist
	Parameters
	----------
	path : string
		"gid" của sheet M3U Playlist
	tracking_string : string
		 Tên dễ đọc của view
	'''
	GA(  # tracking
		"M3U Section - %s" % tracking_string,
		"/m3u-section/%s" % path
	)
	items = getItems(path)
	for item in items:
		# Chỉnh lại thành m3u item
		item["path"] = item["path"].replace("/play/", "/m3u/")
		if "is_playable" in item:
			del item["is_playable"]
		if "playable" in item:
			del item["playable"]
	return plugin.finish(AddTracking(items))


@plugin.route('/m3u/<path>', name="m3u_default")
@plugin.route('/m3u/<path>/<tracking_string>')
def M3U(path="0", tracking_string="M3U"):
	'''
	Liệt kê danh sách các item của sheet M3U Playlist
	Parameters
	----------
	path : string
		Link chưa nội dung playlist m3u
	tracking_string : string
		 Tên dễ đọc của view
	'''
	GA(  # tracking
		"M3U - %s" % tracking_string,
		"/m3u/%s" % path
	)

	items = M3UToItems(path)
	return plugin.finish(AddTracking(items))

@plugin.route('/install-repo/<path>/<tracking_string>')
def InstallRepo(path="0", tracking_string=""):
	'''
	Cài đặt repo
	Parameters
	----------
	path : string
		Nếu truyền "gid" của Repositories sheet:
			Cài tự động toàn bộ repo trong Repositories sheet
		Nếu truyền link download zip repo
			Download và cài zip repo đó
	tracking_string : string
		 Tên dễ đọc của view
	'''
	GA(  # tracking
		"Install Repo - %s" % tracking_string,
		"/install-repo/%s" % path
	)
	if path.isdigit():  # xác định GID
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Vui lòng đợi', 'Bắt đầu cài repo', 'Đang tải...')
		items = getItems(path)
		total = len(items)
		i = 0
		failed = []
		installed = []
		for item in items:
			done = int(100 * i / total)
			pDialog.update(done, 'Đang tải', item["label"] + '...')
			if ":/" not in item["label2"]:
				result = xbmc.executeJSONRPC(
					'{"jsonrpc":"2.0","method":"Addons.GetAddonDetails", "params":{"addonid":"%s", "properties":["version"]}, "id":1}' % item["label"])
				json_result = json.loads(result)
				if "version" in result and version_cmp(json_result["result"]["addon"]["version"], item["label2"]) >= 0:
					pass
				else:
					try:
						item["path"] = "http" + item["path"].split("http")[-1]
						download(urllib.unquote_plus(item["path"]), item["label"])
						installed += [item["label"].encode("utf-8")]
					except:
						failed += [item["label"].encode("utf-8")]
			else:
				if not os.path.exists(xbmc.translatePath(item["label2"])):
					try:
						item["path"] = "http" + item["path"].split("http")[-1]
						download(urllib.unquote_plus(item["path"]), item["label2"])
						installed += [item["label"].encode("utf-8")]
					except:
						failed += [item["label"].encode("utf-8")]

			if pDialog.iscanceled():
				break
			i += 1
		pDialog.close()
		if len(failed) > 0:
			dlg = xbmcgui.Dialog()
			s = "Không thể cài các rep sau:\n[COLOR orange]%s[/COLOR]" % "\n".join(
				failed)
			dlg.ok('Chú ý: Không cài đủ repo!', s)
		else:
			dlg = xbmcgui.Dialog()
			s = "Tất cả repo đã được cài thành công\n%s" % "\n".join(installed)
			dlg.ok('Cài Repo thành công!', s)

	else:  # cài repo riêng lẻ
		try:
			download(path, "")
			dlg = xbmcgui.Dialog()
			s = "Repo %s đã được cài thành công" % tracking_string
			dlg.ok('Cài Repo thành công!', s)
		except:
			dlg = xbmcgui.Dialog()
			s = "Vùi lòng thử cài lại lần sau"
			dlg.ok('Cài repo thất bại!', s)

	xbmc.executebuiltin("XBMC.UpdateLocalAddons()")
	xbmc.executebuiltin("XBMC.UpdateAddonRepos()")


@plugin.route('/repo-section/<path>/<tracking_string>')
def RepoSection(path="0", tracking_string=""):
	'''
	Liệt kê các repo
	Parameters
	----------
	path : string
		Link download zip repo.
	tracking_string : string
		Tên dễ đọc của view
	'''
	GA(  # tracking
		"Repo Section - %s" % tracking_string,
		"/repo-section/%s" % path
	)

	items = getItems(path)
	for item in items:
		if "/play/" in item["path"]:
			item["path"] = item["path"].replace("/play/", "/install-repo/")
		# hack xbmcswift2 item to set both is_playable and is_folder to False
		item["is_playable"] = False
	items = AddTracking(items)

	install_all_item = {
		"label": "[COLOR green]Tự động cài tất cả Repo dưới (khuyên dùng)[/COLOR]".decode("utf-8"),
		"path": pluginrootpath + "/install-repo/%s/%s" % (path, urllib.quote_plus("Install all repo")),
		"is_playable": False,
		"info": {"plot": "Bạn nên cài tất cả repo để sử dụng đầy đủ tính năng của [VN Open Playlist]"}
	}
	items = [install_all_item] + items
	return plugin.finish(items)


def download(download_path, repo_id):
	'''
	Parameters
	----------
	path : string
		Link download zip repo.
	repo_id : string
		Tên thư mục của repo để kiểm tra đã cài chưa.
		Mặc định được gán cho item["label2"].
		Truyền "" để bỏ qua Kiểm tra đã cài
	'''
	if repo_id == "":
		repo_id = "temp"
	if ":/" not in repo_id:
		zipfile_path = xbmc.translatePath(os.path.join(tmp, "%s.zip" % repo_id))
		urllib.urlretrieve(download_path, zipfile_path)
		with zipfile.ZipFile(zipfile_path, "r") as z:
			z.extractall(addons_folder)
	else:
		zipfile_path = xbmc.translatePath(
			os.path.join(tmp, "%s.zip" % repo_id.split("/")[-1]))
		urllib.urlretrieve(download_path, zipfile_path)
		with zipfile.ZipFile(zipfile_path, "r") as z:
			z.extractall(xbmc.translatePath("/".join(repo_id.split("/")[:-1])))


def AddTracking(items):
	'''
	Hàm thêm chuỗi tracking cho các item
	Parameters
	----------
	items : list
		Danh sách các item theo chuẩn xbmcswift2.
	'''

	for item in items:
		if "plugin.video.vinh.movies" in item["path"]:
			tmps = item["path"].split("?")
			if len(tmps) == 1:
				tail = ""
			else:
				tail = tmps[1]
			item["path"] = "%s/%s?%s" % (tmps[0],
			                             urllib.quote_plus(item["label"]), tail)
	return items


@plugin.route('/showimage/<url>/<tracking_string>')
def showimage(url, tracking_string):
	xbmc.executebuiltin("ShowPicture(%s)" % urllib.unquote_plus(url))


@plugin.route('/executebuiltin/<path>/<tracking_string>')
def execbuiltin(path, tracking_string=""):
	GA(  # tracking
		"Execute Builtin - %s" % tracking_string,
		"/repo-execbuiltin/%s" % path
	)
	try:
		xbmc.executebuiltin('XBMC.RunPlugin(%s)' % urllib.unquote_plus(path))
	except:
		pass


@plugin.route('/play/<url>/<title>')
def play_url(url, title=""):
	GA("Play [%s]" % title, "/play/%s/%s" % (title, url))
	url = get_playable_url(url) #will go to get_playable_url(url)
	#Hack for some buggy redirect link #But Buggy with mediafire, then disable it for now.
	#try:
		#http = httplib2.Http(disable_ssl_certificate_validation=True)
		#http.follow_redirects = True
		#(resp, content) = http.request(
		#	url, "HEAD"
		#)
		#url = resp['content-location']
	#except:
		#pass	
	#####will get error handle if call plugin.set_resolved_url 2 times

	headers1 = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
		'Accept-Encoding': 'gzip, deflate',
	}
	headers2 = {
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
			'Referer':url,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
		}
	vsub = 'https://docs.google.com/spreadsheets/d/1NwDGsRUhlXvvCPT3ToXJzn450Nto6FyLLBMucdxK13A/export?format=tsv&gid=0'
	if "sub" in plugin.request.args:
		plugin.set_resolved_url(url, subtitles=plugin.request.args["sub"][0])
	elif 'chaturbate.com' in url:
		source = requests.get(url, headers=headers1).text
		try:
			url = re.findall('"src=\'(.*?)\'', source)[0]
			if 'm3u' not in url:
				return notice('This Model is Private Show Now!!', 'Please choose other model!!', 'Con ghệ này đang chat private, chọn con khác đi!!')
		except:
			return notice('This Model is Offline Now!!', 'Please choose other model!!', 'Con ghệ này off rồi, chọn con khác đi!!')
		plugin.set_resolved_url(url, subtitles=vsub)
	#elif 'topphimhd' in url or 'topphimhd.info' in url:
	#elif url.startswith('http://topphimhd') or url.startswith('http://topphimhdz.com'):
	elif any(url.startswith(domain) for domain in ['http://topphimhd', 'http://topphimhdz.com', 'http://topphimhdz.net', 'http://get.topphimhd.info']):
		source = requests.get(url, headers=headers2).text
		try:
			linkstream = re.findall('embed-responsive-item" src="(.*?)"', source)[0]
			source3 = requests.get(linkstream, headers=headers2).text
			source3 = source3.encode('utf8') #source3.text has unicode (special char) or url has unicode, have to do replace(' ', '%20'), and encode not safe char in url next
			#link = re.findall('urlVideo = \'(.*?)\'', source3)[0]#+'|Referer='+linkstream+'&User-Agent=iPad'
			link = re.findall('file: \'(.*?)\'', source3)[0]#+'|Referer='+linkstream+'&User-Agent=iPad'
			link = link.replace(' ', '%20').replace('https:/vuighe.org', 'https://vuighe.org')
			#url = urllib.quote_plus(link, safe="%/:=&?~#+!$,;'@()*[]")+'|Referer='+linkstream+'&User-Agent=iPad'
			link = urllib.quote_plus(link, safe="%/:=&?~#+!$,;'@()*[]") #encode only not in safe, python 3: link=urllib.parse.quote_plus(link, "%/:=&?~#+!$,;'@()*[]")
			url = link+'|Referer='+linkstream+'&User-Agent=iPad'
		except:
			import resolveurl
			link_okru = re.findall('(https://ok.ru.*?) ', source)[0]
			url = resolveurl.resolve(link_okru)
		plugin.set_resolved_url(url, subtitles=vsub)

	elif url.startswith('https://phimhdonlinetv.com')  or url.startswith('https://phimhdonlinetv1.com'):
		source = requests.get(url, headers=headers1).text
		source = source.encode('utf8') #source.text has unicode (special char) or url has unicode, have to do replace(' ', '%20'), and encode not safe char in url next
		url = re.findall('source src="(.*?)"', source)[0]
		url = url.replace(' ', '%20')
		url = urllib.quote_plus(url, safe="%/:=&?~#+!$,;'@()*[]") #encode only not in safe, python 3: link=urllib.parse.quote_plus(link, "%/:=&?~#+!$,;'@()*[]")
		plugin.set_resolved_url(url, subtitles=vsub)

	elif 'cam2cam.com' in url:
		source = requests.get(url, headers=headers1).text
		try:
			linkstream = 'https://cam2cam.com'+(re.findall('iframe.src = \'(.*?)\'', source)[0])
		except:
			return notice('This Model is Offline Now!!', 'Please choose other model!!', 'Con ghệ này off rồi, chọn con khác đi!!')
		source2 = requests.get(linkstream, headers=headers1).text
		linkstream2 = re.findall('data-manifesturl="(.*?)"', source2)[0]
		source3 = requests.get(linkstream2, headers=headers1).text
		#url = re.findall('location\":\"(https://.*?1280.*?index.m3u8)\"', source3)[0]
		try:
			url = re.findall('location\":\"(https://.*?index.m3u8)\"', source3)[0]
		except:
			return notice('This Model is Private Show Now!!', 'Please choose other model!!', 'Con ghệ này đang chat private, chọn con khác đi!!')
		plugin.set_resolved_url(url, subtitles=vsub)
	
#	elif url.startswith('http://rauma.tv/'):
#		source  = requests.get(url, headers=headers1).text
#		url = re.findall('linkStream=\'(.*?)\'', source)[0]
#		plugin.set_resolved_url(url, subtitles=vsub)
	
	elif url.startswith('http://keonhacai.net'):
		source = requests.get(url, headers=headers1).text
		try:
			link = re.findall('(http://tv.keonhacai.net.*?php)',source)[0]
		except:
			link = re.findall('(http://tv.keonhacai.net.*?) ',source)[0]
		source2 = requests.get(link, headers=headers2).text
		try:
			link2 = re.findall('(http://hdstreams.*?php)',source2)[0]
			source3 = requests.get(link2, headers=headers2).text
			link3 = re.findall('window.atob\(\'(.*?)\'',source3)[0]
			url = base64.b64decode(link3)+'|User-Agent=iPad&Referer='+link2
		except:
			link2 = re.findall('src="(.*?)"',source2)[0]
			source3 = requests.get(link2, headers=headers2).text
			url = re.findall('(http.*?m3u8)',source3)[0]
		plugin.set_resolved_url(url, subtitles=vsub)

	elif url.startswith('https://tructiepbongda.vip'):
		source = requests.get(url, headers=headers1).text
		try:
			url = re.findall('file: \'(.*?)\'',source)[0]
		except:
			notice1 = 'This event has not started yet!'
			notice2 = '[COLOR yellow]Chưa Tới Giờ Phát, This event has not started yet.[/COLOR]'
			notice3 = '[COLOR yellow]Xin Trở Lại Sau, Please Come Back Later![/COLOR]'
			notice(notice1, notice2, notice3)
		plugin.set_resolved_url(url, subtitles=vsub)

	elif url.startswith('https://live.90phut.tv') or url.startswith('https://live1.90p.tv'):
		source = requests.get(url, headers=headers1).text
		url = re.findall('file: "(.*?)"',source)[0]+'|User-Agent=iPad&Referer='+url
		plugin.set_resolved_url(url, subtitles=vsub)

#	elif url.startswith('https://www.film2movie.ws'):
#		source = requests.get(url, headers=headers2).text
#		try:
#			url = re.findall('font-family: wdgoogle;">.*?<strong>\| <a href="(.*?)"', source)[1]
#		except:
#			try:
#				url = re.findall('font-family: wdgoogle;">.*?<strong>\| <a href="(.*?)"', source)[0]
#			except:
#				try:
#					url = re.findall('<strong>\| </strong><a href="(.*?)"', source)[0]
#				except:
#					try:
#						url = re.findall('<strong>\| <a href="(.*?)"', source)[0]
#					except:
#						try:
#							url = re.findall('</span> : \| <a href="(.*?)"', source)[0]
#						except:
#							url = re.findall('center;"><a href="(.*?)"', source)[0]
#		plugin.set_resolved_url(url, subtitles=vsub)
	
	elif url.startswith('https://bilumoi.com') or url.startswith('https://bilutv.org') or url.startswith('https://bilutvz.com') or url.startswith('https://zingtvz.org'):
		#url2 = 'https://bilumoi.com/ajax/player'
		#url2 = 'https://bilutv.org/ajax/player'
		url2 = 'https://zingtvz.org/ajax/player'
		source = requests.get(url, headers=headers2).text
		movie_id = re.findall('MovieID = \'(.*?)\'', source)[0]
		ep_id = re.findall('EpisodeID = \'(.*?)\'', source)[0]
#		source_all = ''
		#for n in range (4):
#		for n in range(3, -1 , -1): #4 Servers
		for n in range(0, 6): #6 Servers
			n = str(n)
			data = {'id': movie_id, 'ep': ep_id, 'sv': n}
			source = requests.post(url2, data = data, verify = False).text
			source = source.replace('\\', '')
			try:
				url = re.findall('file":"(http.*?)"', source)[0] #gdrive
				plugin.set_resolved_url(url, subtitles=vsub)
			except:
				try:
					url = re.findall('file": "(http.*?)"', source)[-1]
					plugin.set_resolved_url(url, subtitles=vsub)
				except:
					pass
			try:
				link = re.findall('src="(https://www.fembed.com/v.*?)"', source)[0]
				linkapi = link.replace('https://www.fembed.com/v', 'https://www.fembed.com/api/source')
				source3 = requests.post(linkapi, data = {'d': 'www.fembed.com', 'r': ''}).text
				response = json.loads(source3)
				response = response['data']
				url = response[-1]['file']
				plugin.set_resolved_url(url, subtitles=vsub)
			except:
				pass
			try:
				import resolveurl
				link = re.findall('src="(https://ok.ru.*?)"', source)[0]
				url = resolveurl.resolve(link)
				plugin.set_resolved_url(url, subtitles=vsub)
			except:
				pass

#			source_all += source
#		try:
#			link = re.findall('file":"(http.*?)"', source_all)[-1]
#			url = link.replace('\\', '')
#		except:
#			try:
#				link = re.findall('src="(https://www.fembed.com/v.*?)"', source_all)[0]
#				linkapi = link.replace('https://www.fembed.com/v', 'https://www.fembed.com/api/source')
#				source3 = requests.post(linkapi, data = {'d': 'www.fembed.com', 'r': ''}).text
#				response = json.loads(source3)
#				response = response['data']
#				url = response[-1]['file']
#			except:
#				import resolveurl
#				link = re.findall('src="(https://ok.ru.*?)"', source_all)[0]
#				url = resolveurl.resolve(link)
#				#url = 'plugin://plugin.video.live.streamspro/play/?url='+urllib.quote_plus(link)+'&mode=19'
		#plugin.set_resolved_url(url, subtitles=vsub)

	elif url.startswith('http://www.hdmoi.net'):
		url2 = 'http://www.hdmoi.net/wp-admin/admin-ajax.php'
		source = requests.get(url, headers=headers1).text
		post_id = re.findall('post_id: (.*?),', source)[0]
		episode = re.findall('episode: (.*?),', source)[0]
		server = re.findall('server: (.*?),', source)[0]
		data = {'action':'halim_ajax_player','nonce':'dabd3ae39f','episode':episode,'server':server,'postid':post_id}
		source2 = requests.post(url2, data=data, verify = False).text
		if 'ok.ru' in source2:
			import resolveurl
			linkstream = 'https:'+re.findall('src="(.*?)"', source2)[0]
			linkstream = resolveurl.resolve(linkstream)
		elif 'googlevideo.com' in source2:
			source2 = source2.replace('\\','')
			linkstream = re.findall('file":"(.*?)"', source2)[0]
		else:
			try:
				linkstream = re.findall('file": "(.*?)"', source2)[0]+'|User-Agent=iPad'
			except:
				respone = re.findall('sources: \[(.*?)\]', source2)[0]
				link = json.loads(respone)['file']
				source3 = requests.get(link, headers=headers1).text
				link_re = re.findall('\n(.*?m3u8)', source3)[0]
				link_long = link.rfind('/')
				link_id = link[:link_long+1]
				linkstream = link_id+link_re+'|User-Agent=iPad'
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	#elif url.startswith('http://www.khmerdrama') or url.startswith('http://www.khmeravenue'):
	elif 'khmersearch' in url or 'khmerdrama' in url or 'khmeravenue' in url:
		import resolveurl
		source = requests.get(url, headers=headers2).text
		url = re.findall('"file": "(.*?)"', source)[0]
		url = resolveurl.resolve(url)
		plugin.set_resolved_url(url, subtitles=vsub)

	elif url.startswith('http://60fps'):
		source = requests.get(url, headers=headers2).text
		try:
			linkstream = re.findall('(http.*?m3u8.*?)\'', source)[0]
		except:
			link = re.findall('title" href="(.*?)"', source)[0]
			source2 = requests.get(link, headers=headers2).text
			linkstream = re.findall('(http.*?m3u8.*?)\'', source2)[0]
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	#elif url.startswith('http://nbastreams') or url.startswith('http://crackstreams') or url.startswith('http://givemereddit.stream') or url.startswith('http://crackstreams.is'):
	elif url.startswith('http://crackstreams.is') or url.startswith('http://nbastreams.site'):
		source = requests.get(url, headers=headers2).text
		try:
			link = re.findall('<iframe.*?width.*?src="(.*?)"', source)[0]
		except:
			link = re.findall('<iframe.*?src="(.*?)"', source)[0]
		if link.startswith('video'):
			link = url+link
		#if link.startswith('https://www.youtube.com'):
			#keyid = re.findall('/(\w+)$', link)[0]
			#linkstream = 'plugin://plugin.video.youtube/play/?video_id='+keyid
			#plugin.set_resolved_url(linkstream, subtitles=vsub)
		source2 = requests.get(link, headers=headers2).text
		source2 = source2.replace("'", '"')
		try:
			linkstream = re.findall('source: "(http.*?m3u8.*?)"', source2)[0]+'|User-Agent=iPad&Referer='+link
		except:
			link2 = re.findall('iframe.*?src="(.*?)"', source2)[0]
			source3 = requests.get(link2, headers=headers2).text
			source3 = source3.replace("'", '"')
			linkstream = re.findall('(http.*?m3u8.*?)"', source3)[0]+'|User-Agent=iPad&Referer='+link2
	#	try:
	#		linkstream = re.findall('(http.*?m3u8.*?)"', source2)[0]+'|User-Agent=iPad&Referer='+link
	#	except:
	#		link2 = re.findall('atob\("(.*?)"', source2)[0]
	#		linkstream = base64.b64decode(link2)+'|User-Agent=iPad&Referer='+link
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	elif any(url.startswith(domain) for domain in ['http://crackstreams.net', 'http://hd.crackstreams.net', 'http://new.crackstreams.net', 'http://ww3.crackstreams.net', 'http://live13.crackstreams.net']):
		source = requests.get(url, headers=headers2).text
		#link = 'http://live13.crackstreams.net'+re.findall('<iframe.*?src="(.*?)"', source)[0]
		link = re.findall('<iframe.*?src="(.*?)"', source)[0]
		if link.startswith('/'):
			link = 'http://live13.crackstreams.net'+link
		source2 = requests.get(link, headers=headers2).text
		source2 = source2.replace("'", '"')
		link2 = re.findall('iframe.*?src="(.*?)"', source2)[0]
		source3 = requests.get(link2, headers=headers2).text
		source3 = source3.replace("'", '"')
		try:
			linkstream = re.findall('return\(\[(.*?)\].join', source3)[0].replace('"','').replace(',','').replace('\\','')+'|User-Agent=iPad&Referer='+link2
		except:
			linkstream = re.findall('(http.*?m3u8.*?)"', source3)[0]+'|User-Agent=iPad&Referer='+link2
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	elif url.startswith('https://daddylive.live') or url.startswith('https://daddylive.club'):
		source1 = requests.get(url, headers=headers2).text
		#link = re.findall('iframe src="(https://wstream.to.*?)"', source1)[0]
		link = re.findall('iframe src="(.*?)"', source1)[0]
		referer = 'https://daddylive.live/'
		h = {
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
			'Referer':referer,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
		}
		source2 = requests.get(link, headers=h).text
		decode = jsunpack.unpack(re.findall('(eval\(function\(p,a,c,k,e,d.*)',source2)[0]).replace('\\', '')
		linkstream = re.findall('source:.*?"(.*?)"', decode)[0]+'|user-agent=ipad&'+link
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	elif url.startswith('http://6stream.xyz') or url.startswith('http://6streams.tv'):
		source = requests.get(url, headers=headers2).text
		linkstream = re.findall('source: "(.*?)"', source)[0]+'|user-agent=ipad&Referer=http://6stream.xyz'
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	elif 'sublink' in url:
		if '(' in url:
			url = re.compile('<sublink>(.*?)\(.*?</sublink>').findall(url)[:] #for builds.kodiuk.tv
		else:
			url = re.compile('<sublink>(.*?)</sublink>').findall(url)[:]
#		items = [] # for look
#		for path in url_path:
#			if path.startswith('http://dl.upload10') or path.startswith('http://dl2.upload10'):
#				path = pluginrootpath + "/layer2/" + urllib.quote_plus(path) #useless for look only
#			else:
#				path = path
#			items += [path]
#		dialog = xbmcgui.Dialog()
#		choise = dialog.select('Please Choose a Link - Xin Chọn Link', items)
		dialog = xbmcgui.Dialog()
		choise = dialog.select('Please Choose a Link - Xin Chọn Link', url) #url is a list, choise is int, choise is -1, 0, 1, 2, ...
		if choise == -1: #choose cancel
			#return None
			pass
		else:
			#if url[choise].startswith('http://dl.upload10') or url[choise].startswith('http://dl2.upload10'): #url[choise] is url_path first or second .. in the list
			if any(url[choise].startswith(domain) for domain in ['http://dl.upload10', 'http://dl2.upload10', 'http://dl2.uploadzone']):
				return Layer2ToItems(url[choise])
			elif url[choise].startswith('https://clipwatching.com') or url[choise].startswith('https://vidlox.me'):
				return play_url(url[choise])
			else:
				#return play_url(url[choise]) #will get error get addtracking, bc direct link(not list anything) ??
				plugin.set_resolved_url(url[choise], subtitles=vsub)

	elif url.startswith('https://vidlox.me'): #movies upload host
		source = requests.get(url, headers=headers2).text
		linkstream = re.findall('sources: \["(http.*?)"', source)[0]
		plugin.set_resolved_url(linkstream, subtitles=vsub)
	elif url.startswith('https://clipwatching.com'): #movies upload host
		source = requests.get(url, headers=headers2).text
		decode = jsunpack.unpack(re.findall('(eval\(function\(p,a,c,k,e,d.*)',source)[0]).replace('\\', '')
		linkstream = re.findall("file:\"(https.*?)\"", decode)[0]
		plugin.set_resolved_url(linkstream, subtitles=vsub)

	#elif url.startswith('https://ok.ru') or url.startswith('https://www.facebook.com')  or url.startswith('https://www.fembed.com'):
	elif any(url.startswith(domain) for domain in (['https://ok.ru', 'https://www.facebook.com', 'https://www.fembed.com', 'https://vidoza.net', \
		'https://verystream.com', 'https://clicknupload.org', 'https://streamango.com', 'https://yesmovies.network'])):
		import resolveurl
		url = resolveurl.resolve(url)
		plugin.set_resolved_url(url)

	else:
		plugin.set_resolved_url(url)

def notice(
	banner = "Channel is Offline Now - Please Try Again Later",
	line1 = "[COLOR yellow]Đài Hiện Tại Không Phát.[/COLOR]",
	line2 = "[COLOR yellow]Xin Vui Lòng Thử Lại Sau![/COLOR]"
	):
	dlg = xbmcgui.Dialog()
	dlg.ok(banner, line1, line2)
	return notice

def get_playable_url(url):
	headers2 = {
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
			'Referer':url,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
		}

	if "youtube.com/watch" in url:
		match = re.compile(
			'(youtu\.be\/|youtube-nocookie\.com\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v|user)\/))([^\?&"\'>]+)').findall(url)
		yid = match[0][len(match[0])-1].replace('v/', '')
		url = 'plugin://plugin.video.youtube/play/?video_id=%s' % yid
	elif "thvli.vn/backend/cm/detail/" in url:
		get_thvl = "https://docs.google.com/spreadsheets/d/13VzQebjGYac5hxe1I-z1pIvMiNB0gSG7oWJlFHWnqsA/export?format=tsv&gid=1287121588"
		try:
			(resp, content) = http.request(
				get_thvl, "GET"
			)
		except:
			header = "Server quá tải!"
			message = "Xin vui lòng thử lại sau"
			xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' %
			                    (header, message, 10000, ''))
			return ""

		tmps = content.split('\n')
		random.shuffle(tmps)
		for tmp in tmps:
			try:
				thvl_headers = {
					'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.3; WOW64; Trident/7.0)',
					"Accept-Encoding": "gzip, deflate, br",
					'Accept': 'application/json',
					'Authorization': tmp.decode('base64')
				}

				(resp, content) = http.request(
					url, "GET", headers=thvl_headers
				)
				resp_json = json.loads(content)
				if "link_play" in resp_json:
					return resp_json["link_play"]
			except:
				pass

	#Open youtube settings, enable MPEG-Dash to play youtube live	
	elif "youtube.com/embed/" in url:		
		yt_addon = xbmcaddon.Addon('plugin.video.youtube')
		if yt_addon.getSetting('kodion.video.quality.mpd') != 'true':
			dialog = xbmcgui.Dialog()
			yes = dialog.yesno(
				'This Channel Need to Enable MPEG-DASH to Play!\n',
				'[COLOR yellow]Please Click OK, Choose MPEG-DASH -> Select Use MPEG-DASH -> Click OK[/COLOR]',
				yeslabel='OK',
				nolabel='CANCEL'
				)
			if yes:
				yt_settings = xbmcaddon.Addon('plugin.video.youtube').openSettings()
				xbmc.executebuiltin('yt_settings')
		else:
			match = re.compile(
				'(youtu\.be\/|youtube-nocookie\.com\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v|user)\/))([^\?&"\'>]+)').findall(url)
			yid = match[0][len(match[0])-1].replace('v/', '')
			url = 'plugin://plugin.video.youtube/play/?video_id=%s' % yid

	#Open LSP settings enable regex
	elif "enableregex" in url:		
		lsp_addon = xbmcaddon.Addon('plugin.video.live.streamspro')
		lsp_settings = xbmcaddon.Addon('plugin.video.live.streamspro').openSettings()
		xbmc.executebuiltin('lsp_settings')

	elif "openmobdro" in url and apk:
		#apk = xbmc.getCondVisibility('system.platform.android')
		xbmc.executebuiltin('StartAndroidActivity(com.mobdro.android)')

	elif "sphim.tv" in url:
		http.follow_redirects = False
		get_sphim = "https://docs.google.com/spreadsheets/d/13VzQebjGYac5hxe1I-z1pIvMiNB0gSG7oWJlFHWnqsA/export?format=tsv&gid=1082544232"
		try:
			(resp, content) = http.request(
				get_sphim, "GET"
			)
		except:
			header = "Server quá tải!"
			message = "Xin vui lòng thử lại sau"
			xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' %
			                    (header, message, 10000, ''))
			return ""

		tmps = content.split('\n')
		random.shuffle(tmps)
		for tmp in tmps:
			try:
				sphim_headers = {
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
					"Accept-Encoding": "gzip, deflate",
					'Cookie': tmp.decode("base64")
				}

				(resp, content) = http.request(
					url, "GET", headers=sphim_headers
				)
				match = re.search('"(http.+?\.smil/playlist.m3u8.+?)"', content)
				if match:
					return match.group(1)
			except:
				pass
	elif url.startswith("acestream://") or url.endswith(".acelive") or "arenavision.in" in url:
		if "arenavision.in" in url:
			h = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
				'Cookie': '__cfduid=d36d59e9714c527d920417ed5bbc9315e1496259947; beget=begetok; ads_smrt_popunder=1%7CSat%2C%2003%20Jun%202017%2018%3A57%3A05%20GMT; 141054_245550_1rhpmin=yes; 141054_245550_1rhpmax=4|Sat%2C%2003%20Jun%202017%2018%3A57%3A14%20GMT; has_js=1; _ga=GA1.2.652127938.1496259947; _gid=GA1.2.653920302.1496429805; _gat=1',
				'Accept-Encoding': 'gzip, deflate'
			}
			(resp, content) = http.request(
				url,
				"GET", headers=h
			)
			url = re.search('(acestream://.+?)"', content).group(1)
		try:
			(resp, content) = http.request(
				"http://localhost:6878/webui/api/service",
				"HEAD"
			)
			url = url.replace(
				"acestream://", "http://localhost:6878/ace/getstream?id=") + "&.mp4"
			if url.endswith(".acelive"):
				url = "http://localhost:6878/ace/getstream?url=" + \
					urllib.quote_plus(url) + "&.mp4"
		except:
			url = 'plugin://program.plexus/?url=%s&mode=1&name=P2PStream&iconimage=' % urllib.quote_plus(
				url)
	elif any(domain in url for domain in ["m.tivi8k.net", "m.xemtvhd.com", "xemtiviso.com"]):
		play_url = ""
		if "xemtiviso.com" not in url:
			for i in range(1, 8):
				try:
					if i > 1:
						range_url = url.replace(".php", "-%s.php" % i)
					h1 = {
						'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
						'Accept-Encoding': 'gzip, deflate',
						'Referer': '%s' % url.replace("/m.", "/www.")
					}
					(resp, content) = http.request(
						range_url,
						"GET", headers=h1,
					)
					content = content.replace("'", '"')

					try:
						play_url = re.search("https*://api.tivi8k.net/.+?'", content).group(1)
						(resp, content) = http.request(
							range_url,
							"GET", headers=h1,
						)
						if "#EXTM3U" in content:
							return play_url
						else:
							return content.strip()
					except:
						pass
					play_url = play_url.replace("q=medium", "q=high")
					if "v4live" in play_url:
						return play_url
				except:
					pass
			try:
				xemtiviso_id = re.search("/(.+?).php", url).group(1).split("-")[0]
				xemtiviso_url = "http://sv2.xemtiviso.com/mimi.php?id=" + xemtiviso_id
				h1 = {
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
					'Accept-Encoding': 'gzip, deflate',
					'Referer': '%s' % xemtiviso_url
				}
				(resp, content) = http.request(
					xemtiviso_url,
					"GET", headers=h1,
				)
				content = content.replace("'", '"')
				play_url = re.search('source\: "(.+?)"', content).group(1)
				play_url = play_url.replace("q=medium", "q=high")
				if "v4live" in play_url:
					return play_url
			except:
				pass
		else:
			try:
				h1 = {
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
					'Accept-Encoding': 'gzip, deflate',
					'Referer': '%s' % url.replace("/m.", "/www.")
				}
				(resp, content) = http.request(
					url,
					"GET", headers=h1,
				)
				content = content.replace("'", '"')
				play_url = re.search('source\: "(.+?)"', content).group(1)
				play_url = play_url.replace("q=medium", "q=high")
			except:
				pass
		return play_url
	elif "vtc.gov.vn" in url:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
			'Accept-Encoding': 'None'
		}
		(resp, content) = http.request(
			url,
			"GET",
			headers=headers
		)
		match = re.search("src: '(.+?)'", content)
		return match.group(1)
	elif "livestream.com" in url:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
			'Accept-Encoding': 'gzip, deflate',
		}
		try:
			if "events" not in url:
				(resp, content) = http.request(
					url,
					"GET", headers=headers,
				)
				match = re.search("accounts/\d+/events/\d+", content)
				url = "https://livestream.com/api/%s" % match.group()
			(resp, content) = http.request(
				url,
				"GET", headers=headers,
			)
			j = json.loads(content)
			url = j["stream_info"]["secure_m3u8_url"]
		except:
			pass
	elif "get-stream.json" in url:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
			'Accept-Encoding': 'gzip, deflate',
		}
		try:
			if "events" not in url:
				(resp, content) = http.request(
					url,
					"GET", headers=headers,
				)
				match = re.search("accounts/\d+/events/\d+", content)
				url = "https://http://118.107.85.21:1340/%s" % match.group()
			(resp, content) = http.request(
				url,
				"GET", headers=headers,
			)
			j = json.loads(content)
			url = j["name"]["url"]
		except:
			pass

#	elif 'ok.ru' in url:
#		import resolveurl
#		return resolveurl.resolve(url)

	elif "onecloud.media" in url:
		ocid = url.split("/")[-1].strip()
		oc_url = "http://onecloud.media/embed/" + ocid
		h = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
			'Accept-Encoding': 'gzip, deflate, sdch',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With': 'XMLHttpRequest',
			'Cookie': 'TimeOut=999999999'}
		(resp, content) = http.request(
			oc_url,
			"POST", headers=h,
			body=urllib.urlencode({'type': 'directLink', 'ip': ''})
		)

		try:
			url = json.loads(content)["list"][0]["file"]
		except:
			header = "Có lỗi xảy ra!"
			message = "Không lấy được link (link hỏng hoặc bị xóa)"
			xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' % (header, message, 10000, ''))
			return ""
	elif "pscp.tv" in url:
		pscpid = re.search("w/(.+?)($|\?)", url).group(1)
		api_url = "https://proxsee.pscp.tv/api/v2/accessVideoPublic?broadcast_id=%s&replay_redirect=false" % pscpid
		(resp, content) = http.request(
			api_url,
			"GET"
		)
		return json.loads(content)["hls_url"]
	elif "google.com" in url:
		url = getGDriveHighestQuality(url)
	elif re.match("^https*\://www\.fshare\.vn/file", url):
		try:
			cred = GetFShareCred()
			if cred:
				fshare_headers = {
					"Accept-Encoding": "gzip, deflate, br",
					'Cookie': 'session_id=%s' % cred["session_id"]
				}
				data = {
					"url": url,
					"token": cred["token"],
					"password": ""
				}

				(resp, content) = http.request(
					convert_ipv4_url("https://api2.fshare.vn/api/session/download"), "POST",
					body=json.dumps(data),
					headers=fshare_headers
				)
				url = json.loads(content)["location"]
				url = convert_ipv4_url(url)
				if resp.status == 404:
					header = "Không lấy được link FShare VIP!"
					message = "Link không tồn tại hoặc file đã bị xóa"
					xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' % (header, message, 10000, ''))
					return None
				(resp, content) = http.request(
					url, "HEAD"
				)
				if '/ERROR' in resp['content-location']:
					header = "Không lấy được link FShare VIP!"
					message = "Link không tồn tại hoặc file đã bị xóa"
					xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' % (header, message, 10000, ''))
					return None
				return url
			return None
		except:	pass
	
	elif url.startswith('https://www.arconaitv.us'):
		source = requests.get(url, headers=headers2).text
		link=re.findall("var _(.+?)</script>",source)[0].strip()
		link=link.replace("eval(", "var a =")
		link="var _" + link[:-1]
		link=link.replace("decodeURIComponent(escape(r))", "r.slice(305,407)")
		return js2py.eval_js(link).replace("'", "")+'|User-Agent=%s' % url

	elif "tv24.vn" in url:
		cid = re.compile('/(\d+)/').findall(url)[0]
		return "plugin://plugin.video.sctv/play/" + cid
	elif "dailymotion.com" in url:
		did = re.compile("/(\w+)$").findall(url)[0]
		return "plugin://plugin.video.dailymotion_com/?url=%s&mode=playVideo" % did
	else:
		if "://" not in url:
			url = None
	return url

def convert_ipv4_url(url):
	host = re.search('//(.+?)(/|\:)', url).group(1)
	addrs = socket.getaddrinfo(host,443)
	ipv4_addrs = [addr[4][0] for addr in addrs if addr[0] == socket.AF_INET]
	url = url.replace(host, ipv4_addrs[0])
	return url

def LoginFShare(uname,pword):
	login_uri = "https://api2.fshare.vn/api/user/login"
	login_uri = convert_ipv4_url(login_uri)
	fshare_headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
		"Accept-Encoding": "gzip, deflate, sdch"
	}
	data = '{"app_key": "L2S7R6ZMagggC5wWkQhX2+aDi467PPuftWUMRFSn","user_email": "%s","password": "%s"}' % (uname, pword)
	resp, cont = http.request(login_uri, "POST", headers=fshare_headers, body=data)
	if "token" in cont and "session_id" in cont:
		plugin.set_setting("cred",cont)
		plugin.set_setting("hash",uname+pword)
		_json = json.loads(cont)
		return _json
	else: return None

def get_fshare_setting(s):
	try:
		return plugin.get_setting(s)
	except: return ""

def GetFShareCred():
	try:
		_hash = get_fshare_setting("hash")
		uname = get_fshare_setting("usernamefshare")
		pword = get_fshare_setting("passwordfshare")
		if _hash != (uname+pword): 
			plugin.set_setting("cred","")
		cred  = json.loads(get_fshare_setting("cred"))
		user = GetFShareUser(cred)
		LoginOKNoti(user["email"], user["level"])
		return cred
	except:
		try:
			uname = get_fshare_setting("usernamefshare")
			pword = get_fshare_setting("passwordfshare")
			cred = LoginFShare(uname,pword)
			user = GetFShareUser(cred)
			LoginOKNoti(user["email"], user["level"])
			return cred
		except: 
			dialog = xbmcgui.Dialog()
			yes = dialog.yesno(
				'Đăng nhập không thành công!\n',
				'[COLOR yellow]Bạn muốn nhập tài khoản FShare VIP bây giờ không?[/COLOR]',
				yeslabel='OK, nhập ngay',
				nolabel='Bỏ qua'
			)
			if yes:
				plugin.open_settings()
				return GetFShareCred()
			return None


def LoginOKNoti(user="",lvl=""):
	header = "Đăng nhập thành công!"
	message = "Chào user [COLOR orange]{}[/COLOR] (lvl [COLOR yellow]{}[/COLOR])".format(user, lvl)
	xbmc.executebuiltin('Notification("{}", "{}", "{}", "")'.format(header, message, "10000"))


def GetFShareUser(cred):
	user_url = "https://api2.fshare.vn/api/user/get"
	user_url = convert_ipv4_url(user_url)
	headers = {
		"Cookie": "session_id=" + cred["session_id"]
	}
	resp, cont = http.request(user_url, "GET", headers=headers)
	user = json.loads(cont)
	return user


def GetPlayLinkFromDriveID(drive_id):
	play_url = "https://drive.google.com/uc?export=mp4&id=%s" % drive_id
	(resp, content) = http.request(
		play_url, "HEAD",
		headers=sheet_headers
	)
	confirm = ""
	try:
		confirm = re.compile(
			'download_warning_.+?=(.+?);').findall(resp['set-cookie'])[0]
	except:
		return play_url
	tail = "|User-Agent=%s&Cookie=%s" % (urllib.quote(
		sheet_headers["User-Agent"]), urllib.quote(resp['set-cookie']))
	play_url = "%s&confirm=%s" % (play_url, confirm) + tail
	return play_url


def GA(title="Home", page="/"):
	'''
	Hàm thống kê lượt sử dụng bằng Google Analytics (GA)
	Parameters
	----------
	title : string
		Tên dễ đọc của view.
	page : string
		Đường dẫn của view.
	'''
	try:
		ga_url = "http://www.google-analytics.com/collect"
		client_id = open(cid_path).read()
		data = {
			'v': '1',
			'tid': 'UA-52209804-5',  # Thay GA id của bạn ở đây
			'cid': client_id,
			't': 'pageview',
			'dp': "VNPlaylist%s" % page,
			'dt': "[VNPlaylist] - %s" % title
		}
		http.request(
			ga_url, "POST",
			body=urllib.urlencode(data)
		)
	except:
		pass


def getGDriveHighestQuality(url):
	(resp, content) = http.request(
		url, "GET",
		headers=sheet_headers
	)
	match = re.compile('(\["fmt_stream_map".+?\])').findall(content)[0]
	prefer_quality = ["38", "37", "46", "22", "45", "18", "43"]
	stream_map = json.loads(match)[1].split(",")
	for q in prefer_quality:
		for stream in stream_map:
			if stream.startswith(q+"|"):
				url = stream.split("|")[1]
				tail = "|User-Agent=%s&Cookie=%s" % (urllib.quote(
					sheet_headers["User-Agent"]), urllib.quote(resp['set-cookie']))
				return url + tail


def cleanHTML(s):
	s = ''.join(s.splitlines()).replace('\'', '"')
	s = s.replace('\n', '')
	s = s.replace('\t', '')
	s = re.sub('  +', ' ', s)
	s = s.replace('> <', '><')
	return s


def version_cmp(local_version, download_version):
	def normalize(v):
		return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]
	return cmp(normalize(local_version), normalize(download_version))


# Tạo client id cho GA tracking
# Tham khảo client id tại https://support.google.com/analytics/answer/6205850?hl=vi
device_path = xbmc.translatePath('special://userdata')
if os.path.exists(device_path) == False:
	os.mkdir(device_path)
cid_path = os.path.join(device_path, 'cid')
if os.path.exists(cid_path) == False:
	with open(cid_path, "w") as f:
		f.write(str(uuid.uuid1()))
if __name__ == '__main__':
	plugin.run()
