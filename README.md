# **THIS PROJECT WILL BE MOVED TO CASINO**

# **Gamba**
## A gambling and stock market simulator backend written in **Python** using **Flask**. 

---

# Features
Gamba stores user data, including username, passwords, money, and assets using SQLAlchemy. Authentication and signup is handled in `account.py`. Gamba uses JWT's to manage user sessions. A `token` must be passed in most games to play. Gambling games endpoints are stored in `games.py`.

The Stock features use real time data using the **Finnhub API**. Live quotes are streamed using Websockets. Purchases are delayed and are batched, which seems reasonable as there is no actual supply / demand.

Since **Finnhub** does not have streaming for option chain data, this will be polled and cached using Redis. Option chain data will also be delayed. I will probably only support option chain for SPY, which is around 8 megabytes per poll.