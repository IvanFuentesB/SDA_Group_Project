 ╔═══╗╔══╗╔═══╗╔╗ ╔╗╔════╗    ╔═══╗╔═╗ ╔╗
 ║╔══╝╚╣╠╝║╔═╗║║║ ║║║╔╗╔╗║    ║╔═╗║║║╚╗║║
 ║╚══╗ ║║ ║║ ╚╝║╚═╝║╚╝║║╚╝    ║║ ║║║╔╗╚╝║
 ║╔══╝ ║║ ║║╔═╗║╔═╗║  ║║      ║║ ║║║║╚╗║║
╔╝╚╗  ╔╣╠╗║╚╩═║║║ ║║ ╔╝╚╗     ║╚═╝║║║ ║║║
╚══╝  ╚══╝╚═══╝╚╝ ╚╝ ╚══╝     ╚═══╝╚╝ ╚═╝
                                         
PyGame Computer Vision 2D Platformer

Install instructions:

Install mosquitto: 1) Go to https://mosquitto.org/download/
		   2) If on windows, select x64 version
		   3) Add mosquito path to environment variables
		
Running game on separate computers:


Camera side instructions
	Open camera_shape_color_detection folder
	Open command prompt and type ip config, then copy the IPv4 address
	In camera_shape_color_detection open config.txt
	change mqtt_ip to your IPv4 address
	Run camera_shape_color_detection.exe
	While the program is running, show different shapes (square, circle, triangle)
	of different colors (red, blue, green, yellow) to the webcam
Game side instructions
	Open game folder
	Open config.txt
	change mqtt_ip to the IPv4 address of the camera side
	open command prompt and type mosquitto_sub -h camera_ipv4address -t "cv/shapes"
	replace camera_ipv4address with the camera's IPv4 address
	Now both camera and game side are connected
	Run game.exe
	Have fun!

Running game on one computer:
	Open camera_shape_color_detection folder
	open config.txt
	change mqtt_ip to localhost (mqtt_ip=localhost)
	Run camera_shape_color_detection.exe
	While the program is running, show different shapes (square, circle, triangle)
	of different colors (red, blue, green, yellow) to the webcam

	Open game folder
	Open config.txt
	change mqtt_ip to localhost (mqtt_ip=localhost)
	open command prompt and type mosquitto_sub -h localhost -t "cv/shapes"
	Now both camera and game side are connected
	Run game.exe
	Have fun!

**If you wish to use your phone as a camera install DroidCam on phone and PC: https://droidcam.app/




