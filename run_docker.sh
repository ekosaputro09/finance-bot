docker kill finance-bot && docker rm finance-bot
docker build -t finance-bot . && docker run --name finance-bot -it -d --restart unless-stopped finance-bot