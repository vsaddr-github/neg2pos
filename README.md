# neg2pos

This is pre-release - no warranties of any kind.
Use only if you understand what you are doing.

Python 3.8 installation and installing required packages is completely on you.

Hint:

Use wsl ver 2, Ubuntu 20.04 , install pyton3 and pip3 - it those words sounds Greek to you - skip the exercise.


Phase 1.  Converting negative JPG into positive image
Usage: python3 env6.py <negative_jpg_image_file_name>

Note: there is line in code (line 82) 
 blend_color = np.array([250, 240, 230])
 
Those RGB numbers correspond to the density of the orange mask on my particular test negative. 
You may measure the density of the mask on your negative with Photoshop picker on rebate area between frames. 
If you dont want to do it use:
 blend_color = np.array([255, 255, 255])
 
 and orange mask will not be removed. Color balance of the output will probably suffer significantly.
