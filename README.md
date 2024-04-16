# intz-dashboard
Dashboard for data cleaning and inspection of a sample of cluster galaxies. 

Deployed to [https://intz-dashboard.onrender.com](https://intz-dashboard.onrender.com). 

For better performance, you can also run using Docker. To create and run a working docker image, uncomment the last line in `src/app.py` to set the apporpriate port and run:

```
docker build -t intz-app .
docker run -p 8000:8080 intz-app
```
