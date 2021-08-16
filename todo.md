# ToDo

### v0
- so much validation (see Flask error handling)
- remove try/except in class_board
- safer password handling
- collapsable login
- read 2 first cards from page

### Near future
- add hoverable icons so you see the card image when you hover over its name (this will probably make the build bigger than 500 MB though)
- make it so this works for a table you aren't a part of (switch how process move works if you don't enter the first cards)
- loading wheel

### Far future
- use spyder to crawl all Innovation games on BGA, from both player perspectives, and come up with recommendations. Probably for this you want a separate engine that this script calls when you get the current gamestate. So send the gamestate to an AWS thing, and it will return 3 potential moves

