var request = require('request');
var cheerio = require('cheerio');
var fs = require('fs');

function UriCache()
{
    this.cache = [];

    var files = fs.readdirSync(__dirname + '/../cache');

    for(var i = 0; i < files.length; i++)
        this.cache.push(files[i]);
}

UriCache.prototype.uriToId = function(uri)
{
    var tokens = uri.split('/');

    return 'HFYA_' + tokens.slice(tokens.length-2, tokens.length).join('_');
};

function msleep(n) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, n);
}

UriCache.prototype.get = function(params, callback)
{
    var id = this.uriToId(params.chap.src);

    params.chap.id = id;

    if(this.cache.indexOf(id) > -1)
    {
        console.log('[\033[92mCached\033[0m] ' + id);
        params.chap.dom = cheerio.load(fs.readFileSync(__dirname + '/../cache/' + id, encoding = 'utf-8'), { decodeEntities: true });
        callback();
        return;
    }

    request({ uri: params.chap.src, headers: { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36' } }, function(parmas, callback, uri_cache) { return function(error, response, body)
    {
        if(!response)
        {
            console.log("archive not ready yet: " + params.chap.id);
            uri_cache.get(params, callback);
            msleep(100);
            return;
        }

        if(response.statusCode === 429)
        {
            console.log("archive waiting " + global.backoff + "ms for: " + params.chap.id);
            console.log(response.request.uri.href);
            console.log(response);
            global.backoff = global.backoff * 2;
            global.backoff = Math.min(global.backoff, 21600000);
            msleep(global.backoff);
            uri_cache.get(params, callback);
            return;
        }

        global.backoff = 1000;

        if(response.statusCode === 503)
        {
            console.log('[\033[91mRetrying\033[0m] ' + params.chap.id);
            uri_cache.get(params, callback);
            return;
        }

        console.log('[\033[93mFetched\033[0m] ' + params.chap.id);
        uri_cache.cache.push(params.chap.id);

        var $ = cheerio.load(body, { decodeEntities: true });
        // var content = $('div.node-content div[property]').contents();
        var content = $('article').children(':not(h1):not(aside)');
        
        $.root().children().remove();
        $.root().append(content);
		$($.root().contents()[0]).remove(); // Remove doctype tag
		
        content = $.root().contents();
        
        for(var i = 0; i < content.length; i++)
        {
        	var e = content[i];
        	
        	if(e.type === 'text' && e.data === '\n\n')
        		e.data = '\n';
        }
        
        params.chap.dom = $;
        
        fs.writeFileSync(__dirname + '/../cache/' + params.chap.id, params.chap.dom.xml(), encoding = 'utf-8');
        
        callback();
    }}(params, callback, this));
};

var uri_cache = new UriCache();

function apply(params, next)
{
    uri_cache.get(params, function()
    {
        next();
    });
}

module.exports =
{
    apply: apply
};
