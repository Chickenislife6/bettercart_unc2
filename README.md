# bettercart_unc
better enrollment for unc

Meant to be used in conjunction with my something website
app.py contains the different api requests possible
ALL REQUIRE AUTHENTICATION
lookup -> looks up a class and returns its status, open -> True, waitlist/closed -> False
add -> adds classes by class id, returns the entire html website from CC 
swap -> swaps 2 classes by class id, returns the entire html website from CC

repeat -> repeats the action until true (only usable for lookup)

TODO: Add a drop request

also must add a cache folder otherwise it'll yell at you or something i think
