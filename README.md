# neg2pos

This is pre-release - no warranties of any kind.
Use only if you understand what you are doing.

Python 3.8 installation and installing required packages is completely on you.

Hint:

On Windows, use wsl ver 2, Ubuntu 20.04 , install pyton3 and pip3 - it those words sounds Greek to you - skip the exercise.


Phase 1.  Converting negative JPG into positive image
Usage: python3 env6.py <negative_jpg_image_file_name>

Note: there is line in code (line 82) 
 blend_color = np.array([250, 240, 230])
 
Those RGB numbers correspond to the density of the orange mask on my particular test negative. 
You may measure the density of the mask on your negative with Photoshop picker on rebate area between frames. 
If you don't want to deal with mask use:

 blend_color = np.array([255, 255, 255])
 
 and orange mask will not be removed. Color balance of the output will probably suffer significantly.

This code is shared by "Vlads Test Target" 

Start every film digitizing/scanning session with checking your setup with "Vlads Test Target". Designed for camera scanning, this essential tool helps you achieve critical focus and uniform sharpness, 
even in the corners of your scans. You'll be able to capture the finest details with ease, ensuring that your final images are of the highest quality possible. Don't miss out on the opportunity to take 
your scanning process to the next level with Vlads Test Target. Your precious images on film negatives and slides deserve the best!
Find "Vlads Test Target" on Amazon, Freestyle Photo, pixl-latr, Valoi sites.
