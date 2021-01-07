# ecs-rogal

Hopefully this will become a roguelike game / roguelike engine in the future.

Right now it's a more of an experimental work-in-progress proof-of-concept tech-demo learning-tool thingy rather than actual game. 

Powered by Python 3 + [python-tcod](https://github.com/libtcod/python-tcod), heavily inspired by wonderful [Rust Roguelike Tutorial](http://bfnightly.bracketproductions.com/rustbook/)

Main goals for this project:
- Use ECS (Entity Component Systems) architecture
- Decouple core game mechanics from rendering / user input code
- Use abstraction layer over `tcod.Console` so it will be easy to switch to other rendering engines (BearLibTerminal? bare curses? who knows what else!)
- Learn as much as possible about game development and design, rogulelikes mechanics, procedural generation, FOV / LOS algorithms, AI, etc
- Have fun!

Work in progress [gallery](https://imgur.com/a/0R8ZwQX)

How to run (Python >= 3.6 required!):

    # Create and activate virtualenv:
    $ python3 -m venv env
    $ source evn/bin/activate
    
    # Install required packages:
    $ pip install -r requirements.txt
    
    # Run:
    $ ./run
    # OR:
    $ python -m rogal
