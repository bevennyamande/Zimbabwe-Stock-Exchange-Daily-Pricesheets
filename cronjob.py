from crontab import CronTab

cron = CronTab(user=True)
job = cron.new(command='scrapper.py')
job.hour.every(24)

cron.write()
