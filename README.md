# hfy_ebook
A tool to create ebooks from /r/HFY posts

Currently only the Jenkinsverse canon posts are supported.

This program consists of two parts. The first part is a Python script that creates a .spec file for you. The second part is node based and that part creates the actual ebook based on the .spec file.

You can skip the Python step by using the spec files in specs/; only specs/HFY_timeline_reading_order.spec is for sure good and fully tested by actually reading it, but specs/HFY_chronological_reading_order.spec is probably also good.  The rest are very old.

There are instructions here for both a local install and docker/podman/etc.

## Local Install

### Installation - Python
Create a virtualenv and install the software in requirements.txt:
```
virtualenv venv
source venv/bin/activate
pip install -r python/requirements.txt
```

After installation of the Python code, you have to modify two variables in the script, so it has your reddit.com API key in it. Open python/hfy.py in your text editor of choice and set REDDIT\_CLIENT\_ID and REDDIT\_CLIENT\_SECRET. You can obtain these by going to https://www.reddit.com/prefs/apps/ and clicking the 'create app' button on the bottom.

### Installation - Node
```
npm install
```

### Running the tools
Run the Python tool to create the .spec file:
```
source venv/bin/activate
python python/hfy.py
```
Then follow that by creating the ebook:
```
node ebook.js HFY_Canon.spec
```
You can find a HTML, epub and LaTeX version in the output folder.

## Docker/Podman Install

This is the Python step which is probably skippable; see above.

$ docker run -it -v$(pwd):/src --rm docker.io/python:3.7 bash
# cd /src
$ pip install -r python/requirements.txt
$ python python/hfy.py https://www.reddit.com/r/HFY/wiki/ref/universes/jenkinsverse/chronological_reading_order/

The node side is for building the book from what you did in the python side, or a spec from the specs/ dir.

Note that the node step calls out to reddit *a lot* and is likely to get rate limited.  I've had to wait overnight in some cases.  There are some sleeps that help for some of it.

$ docker run --rm -it -v $(pwd):/src docker.io/library/node:23-bookworm bash 
# cd /src
# npm install
# npm install request
# node ebook.js specs/HFY_chronological_reading_order.spec
