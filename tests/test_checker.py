

if __name__ == "__main__":
   team = 42
   host = "localhost"
   port = 8000
   max_tick = 10
   for tick in range(max_tick):
       checker = JodlGangChecker(tick, team, host, port)
       assert OK == checker.place_flag()
       for check_tick in range(max(0, tick - 5), tick + 1):
           assert OK == checker.check_flag(check_tick)
       assert OK == checker.check_service()