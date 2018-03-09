# Enno

Wrapper around Evernote's python client that makes it just a little more pleasant to use.


## Get an access token

1. Go [here](http://dev.evernote.com/doc/) and click **GET AN API KEY**.
2. Fill out the information for your Oauth app
3. Create an account on the [development server](https://sandbox.evernote.com/Registration.action)
4. add your key and secret to the environment:

        $ export ENNO_CONSUMER_KEY=...
        $ export ENNO_CONSUMER_SECRET=...

5. Create an access token:

        $ enno oauth --sandbox

6. Export your sandbox access token:

        $ export ENNO_SANDBOX=1
        $ export ENNO_SANDBOX_ACCESS_TOKEN=...

7. When you are ready to use your app on your actual live evernote, go [here](http://dev.evernote.com/support/) and click **Activate an API Key**.

8. When your api key is activated you can then get a real access token:

        $ enno oauth
        $ export ENNO_SANDBOX=0
        $ export ENNO_ACCESS_TOKEN=...


## Querying notes

```python
from enno import Note

# get the first 10 notes containing foo in the title
q = Note.query.in_title("foo").limit(10)
for n in q.get():
    print(n.title)
```


## Creating notes

save text:

```python
from enno import Note

n = Note()

n.title = "this is the title"
n.plain = "this is the content"
n.save()
print(n.guid)
```

Save html:

```python
n = Note()

n.title = "this is the title"
n.html = "<p>this is the content</p>"
n.save()
print(n.guid)
```

Evernote saves its notes in a format called [ENML](http://dev.evernote.com/doc/articles/enml.php), this is available in the `.content` property:

```python
n = Note()

n.title = "this is the title"
n.html = "<p>this is the content</p>"
print(n.content) # the html will have been converted to enml
```


## Creating Notebooks

```python
from enno import Notebook

nb = Notebook()

nb.name = "foo bar"
nb.save()
print(nb.guid)
```


## Installation

Use pip:

    $ pip install enno

To get the latest and greatest:

    $ pip install git+https://github.com/jaymon/enno#egg=enno

