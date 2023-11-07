# Mercari_Monitor
# A monitor based on Python and Selenuim that can monitor product list changes for specific keywords in Mercari.

# Mercari Monitor

# Preparation:
# 1. install all the packages need to be imported.
# 2. make sure your chrome is on the last version (>115).
# 3. create a telegram bot and get its token (can get it when the bot is created),
# and chat_id(please refer to https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id).
# 4. replace the keyword, token and chat_id with your own content.
# 5. run the .py code and check your telegram bot.

# Note:
# 1. this code can be run on linux and Windows devices, but larger RAM (at least 1G) is recommended.
#
# 2. selenium and chrome may generate log files, which need to be cleared regularly. my solution: add the line below
# to your crontab: 0 */2 * * * find /tmp -type d -name ".org.chromium*" -exec rm -rf {} +
#
# 3. mercari seems to have modified its search strategy recently.
#   it's normal if irrelevant products are frequently detected. machine learning may be adopted to address this problem.
#
