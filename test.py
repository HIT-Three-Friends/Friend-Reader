import urllib.request
uri_base = "https://api.ltp-cloud.com/analysis/?"
api_key  = "F1a5e3k9w7UPcXnfjcETgQFTwWZVoCvKwIwEEtmQ"
text     = "我爱北京天安门"
# Note that if your text contain special characters such as linefeed or '&',
# you need to use urlencode to encode your data
format   = 'plain'
pattern  = "all"
text = urllib.request.quote(text)
url      = (uri_base
            + "api_key=" + api_key + "&"
            + "text="    + text    + "&"
            + "format="  + format  + "&"
            + "pattern=" + 'pos')
print(url)
response = urllib.request.urlopen(url)
content  = response.read().strip().decode('utf8')
print (content)
ans = content.split()
for a in ans:
    if a[-3:] == "_ns":
        print(a.replace('_ns',''))
