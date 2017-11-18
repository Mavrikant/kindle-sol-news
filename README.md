# kindle-sol-news
Sent columns on sol.org.tr to Kindle e-reader


#Modified version of https://github.com/mr-karan/webkin
read webkin's documents.



#cron entry:
0 * * * *  cd /home/user/kindle-sol-news/ && python3 kindle-sol-news.py >> /home/user/kindle-sol-news/cron_log.txt 2>&1
