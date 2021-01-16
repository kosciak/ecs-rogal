# ecs-rogal

Hopefully this will become a roguelike game / roguelike engine in the future.

Right now it's a more of an experimental work-in-progress proof-of-concept tech-demo learning-tool thing rather than actual game. 

Powered by Python 3 + [python-tcod](https://github.com/libtcod/python-tcod), heavily inspired by wonderful [Rust Roguelike Tutorial](http://bfnightly.bracketproductions.com/rustbook/)

## Main development goals
- Use [ECS](https://en.wikipedia.org/wiki/Entity_component_system) architecture
- Decouple core game mechanics from rendering / user input code as much as possible
- Use abstraction layer over `tcod.Console` so it will be easy to switch to other rendering engines (BearLibTerminal? bare curses? who knows what else!)
- Learn as much as possible about game development and design, rogulelikes mechanics, procedural generation, FOV / LOS algorithms, AI, etc
- Have fun and experiment!
- Maybe, just maybe someday turn it into playable and fun game

Work in progress [gallery](https://imgur.com/a/0R8ZwQX)

## How to run
Python >= 3.6 required!

#### Linux:

    # Create and activate virtualenv:
    $ python3 -m venv env
    $ source evn/bin/activate
    
    # Install required packages:
    $ pip install -r requirements.txt
    
    # Run:
    $ ./run
    # OR:
    $ python -m rogal

#### Windows
Huh... That's a very good question :)

**WARNING!** Things might break, things might not work as expected, things might change in any time! 
