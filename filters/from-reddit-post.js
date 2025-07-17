var request = require('request');
var cheerio = require('cheerio');
var marked = require('marked');
var fs = require('fs');

marked.escape = function(html, encode)
{
    return html;
}

function getContinuations(set, author)
{
    // Recursively search through comments, looking for plausible continuations
    for(var key in set)
    {
        var c = set[key].data;

        if(c.author === author && c.body_html.length > 1000)
        {
            var html = '\n\n\n------\n\n\n' + c.body;

            if(c.replies.data)
                html += getContinuations(c.replies.data.children, author);

            return html;
        }
    }

    return '';
}

function getPostMarkdown(json)
{
    var post = json[0].data.children[0].data;
    var author = post.author;
    var md = post.selftext + getContinuations(json[1].data.children, author);

    return md.replace(/&amp;/g, '&');
}

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

    return tokens.slice(4, tokens.length - 1).join('_');
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

    request({ uri: params.chap.src + '.json', headers: { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36' } }, function(parmas, callback, uri_cache) { return function(error, response, body)
    {
        if(!response)
        {
            console.log("reddit not ready yet: " + params.chap.id);
            uri_cache.get(params, callback);
            msleep(100);
            return;
        }

        if(response.statusCode === 429)
        {
            console.log("reddit waiting " + global.backoff + "ms for: " + params.chap.id);
            console.log(response.request.uri.href);
            // console.log("caseless");
            // console.log(response.caseless.dict);
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

        var md = getPostMarkdown(JSON.parse(body));
        var html = marked(md);

        params.chap.dom = cheerio.load(html, { decodeEntities: true });
        
        fs.writeFileSync(__dirname + '/../cache/' + params.chap.id, params.chap.dom.html(), encoding = 'utf-8');
        
        if(false)
        {
            fs.writeFileSync(__dirname + '/../cache/' + params.chap.id + '.marked', html, encoding = 'utf-8');
            fs.writeFileSync(__dirname + '/../cache/' + params.chap.id + '.md', md, encoding = 'utf-8');
        }
        
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
