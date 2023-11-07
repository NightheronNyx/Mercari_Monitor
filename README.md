<h1>Mercari_Monitor メルカリ商品リストモニター</h1>
A monitor based on Python and Selenuim that can monitor product list changes for specific keywords in Mercari.

<h2>Preparation:</h2>
1. install all the packages need to be imported.<br>
2. make sure your chrome is on the last version (>115).<br>
3. create a telegram bot and get its token (can get it when the bot is created), and chat_id (please refer to https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id).<br>
4. replace the keyword, token and chat_id with your own content.<br>
5. run the .py code and check your telegram bot.<br>

<h2>Note:</h2>
1. this code can be run on linux and Windows devices, but larger RAM (at least 1G) is recommended.<br>
2. selenium and chrome may generate log files, which need to be cleared regularly. my solution: add the line below<br>
to your crontab: 0 */2 * * * find /tmp -type d -name ".org.chromium*" -exec rm -rf {} +
<br>
3. mercari seems to have modified its search strategy recently. it's normal if irrelevant products are frequently detected. machine learning may be adopted to address this problem.

