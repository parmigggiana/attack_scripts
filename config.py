log_level = "debug"
team_id = 77
highest_id = 1
TEAM_TOKEN = "b0d9d5b0307be878aa00e935e230d2d"
max_time = 10  # time for a single thread to issue a warning. It will still wait for it to complete
tick_duration = 20  # gametick duration
flag_regex = "[A-Z0-9]{31}="
baseip = "10.60.{id}.1"
db_url = "mongodb://localhost:27017/"
flag_submission_delay = (
    120  # Every 10 seconds all new flags are submitted to the gameserver
)
