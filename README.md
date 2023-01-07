# IA-Bad_Fruit_Detector
Spoiled fruit detector in real time using convolutional neural networks and FreeRTOS. It runs on the ESP32-CAM microcontroller and uses a python interface to display the image taken and the inference results.

Instructions for running the system
For the correct execution of the system it is necessary to carry out a series of steps
ordered. The steps to follow are detailed below:
1. Install the SerialTransfer library in the Python environment being used.
Do the same but in the Arduino environment (Arduino IDE) through the manager
libraries.
2. Install the PIL and numpy libraries in the Python environment.
3. Download the provided files, the folder detector_frutas_freertos and the file
GUI_detector_fruits_v1.2.py
4. Open the arduino project (detector_frutas_freertos.ino) and the Python file.
5. Connect the USB cable from the FTDI programmer to the computer. In the Arduino IDE
select the AI-Thinker ESP32-CAM board, for which you must have the
corresponding package.
6. Connect the Jumper of figure 2 to the microcontroller, then from the arduino IDE
upload the code to the board.
7. Disconnect the Jumper and unplug the USB cable.
8. Plug the USB cable back in. Wait a few seconds for the code to be
initialize.
9. Run the Python code, after a few seconds you should see the graphical interface.
You will be able to see the data updating every 800ms.
