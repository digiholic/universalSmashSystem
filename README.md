# What is Project TUSSLE?
Have you ever heard of the video game series Super Smash Bros, and thought “This is cool, but why isn’t Character X in this game?” Well, you don’t need to wonder any longer! TUSSLE is a platform fighter that can have literally INFINITE characters!

How is this possible? Why, through the power of Open Source! The game is fully modifiable, and will have a robust and simple character builder to turn your favorite characters into fighters. Grab sprites from that old SNES fighting game you loved, or draw up your own original character to join the tussle!

TUSSLE is currently in alpha, but development is moving quickly! If you want to keep up to date with the changes as they come in, make sure to follow us on twitter [@TUSSLEdev](https://twitter.com/TUSSLEdev) which will be posing a real-time changelog as anything is updated. If you have any questions, or just want to hang out with the community, feel free to check out our [subreddit](https://www.reddit.com/r/projectTUSSLE).

# How to play
**Simple**:

Currently, an unknown bug is preventing the EXE file from compiling. Please use the advanced option below.

~~In the front page, click on "Download Zip" to get an archive of the game. Open it, and run main.exe. This will run the game at it's last stable compiled state. If the exe does not run at all, please submit an issue with the contents of your main.exe.log file. If you would like to run the most recent code, or are running the game on Linux, please see the advanced section.~~

**Advanced**:

After downloading the zip file as described above, run main.py in python. The game runs on python 2 or 3, and requires the modules pygame and numpy.

Windows users:
* Download the Python installer from [python.org](https://www.python.org/downloads/windows/) (NOTE: Download 32-bit Python, even if your computer is 64-bit. Pygame only works with 32 bit python)
* After installing Python, install [Pygame](http://pygame.org/download.shtml) for the version of Python you installed.
* Install [NumPy](http://www.scipy.org/scipylib/download.html)
* Run main.py in python. (If windows does not recognize to open main.py in Python, right click on it, Click Open With -> Choose Another App and navigate to your python directory and select python.exe

Linux users:
* Install python through your package manager, such as `apt-get install python`
* Install pip through your package manager, usually a command like `apt-get install python-pip`
* Run the commands `pip install pygame` and `pip install numpy`
* Navigate to the folder you extracted TUSSLE to and run `python main.py`

Mac users:
* I'm gonna level with you here. I don't have a mac. I've never installed python on a mac. I don't even know if TUSSLE currently actually works on a mac. It shouldn't be too different from Linux, but if you've gotten it working on a mac, please let us know so I can update this section. Sorry for that!

# Controls and Options
By default, TUSSLE's controls are the following:

Player 1 -
* Movement - Arrow Keys
* Physical Attack - Z
* Special Attack - X
* Jump - C
* Shield - A

Player 2 - 
* Movement - IJKL
* Physical Attack - U
* Special Attack - H
* Jump - I
* Shield - O

These controls can be re-bound in the menu in-game, or by modifying the file settings/settings.ini. If you want to use more than two players, it is recommended that you bind them to some left over keys and use a program such as joy2key to control them with external gamepads. Gamepad support is in the works, but is not currently functional.

Inside of the settings file, you can also modify things such as the screen size (NOTE: There are currently some layout bugs with bigger screens, and the camera doesn't zoom in as far, but the game is playable at larger resolutions). There are also Physics Presets inside of the settings/rules folder. These settings are mostly un-implemented and serve as reminders for us to do them later, but they are all planned to be modifiable.

# Installing new modules
Currently, there is no simple character builder, but if you've got some Python chops, you're free to create your own (find out more about how to build characters on our website [projecttussle.com](http://projecttussle.com/))

To install a downloaded character:
* Extract the character folder to fighters

And that's all! If the character is properly formed, it'll be selectable in-game!

For stages:
* Extract the stage folder to stages

Boy is that easy. It's just making them is the hard part at the moment!
