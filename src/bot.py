'''
    Unofficial bot that show current prices of coins of the WAX ecosystem.
    Also you can check your account status of your RAM, CPU and NET.

    This bot was created by Vindezor (ddgra.wam)
'''
from views.flask_views import server
import os

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))