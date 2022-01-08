# splaynet
Flask app for probabilities behind the card game Innovation 

#### setup notes
* chrome buildpack and environment variables set in Heroku dashboard, see [link](https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c)
* this is what i used to get flask and python on heroku [link](https://dev.to/techparida/how-to-deploy-a-flask-app-on-heroku-heb)
* helpful link about cookies in javascript [link](https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript)
* progress-bar example that taught me about event-stream [link](https://gist.github.com/vulcan25/52fe1ba5860d0a0448d99fc74428123e)
* airium lets you build template strings [link](https://pypi.org/project/airium/), but I made them first [link](https://getbootstrap.com/docs/5.0/components/accordion/)

#### reminders for running local

in config.py, set `Debug = True`

Then in two console windows:

```
> flask run
```
and:
```
> rq worker 
```

#### pushing to heroku
Make sure that `Debug = False` in config.py when you push
```
git push heroku origin:master
```