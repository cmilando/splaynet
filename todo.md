# ToDo

- job breaks when move is unknown
- see Dillen comment about reading the logs directly rather than reading page UI

### v0
- so much validation (see Flask error handling)
- remove try/except in class_board
- safer password handling
- collapsable login
- move javascript to separate files
- read 2 first cards from page
- job id printing error, socket breaks etc h18 error, ask Dillen

### Near future
- add hoverable icons so you see the card image when you hover over its name (this will probably make the build bigger than 500 MB though)
- make it so this works for a table you aren't a part of (switch how process move works if you don't enter the first cards)
- loading wheel

### Far future
- use spyder to crawl all Innovation games on BGA, from both player perspectives, and come up with recommendations. Probably for this you want a separate engine that this script calls when you get the current gamestate. So send the gamestate to another heroku site, and it will return 3 potential moves

