"""A file for scanning a video of mario gameplay for jumping
Author: Matthew Byrd
Date created: 8/31/2018
Date last modified: 9/6/2018
"""
import cv2
from TemplateScanner import TemplateScanner

mario_video = cv2.VideoCapture("SuperMarioBros.mp4")

index = 0
export = True

# Slider as to not get all frames of a single jump, instead only getting as close to the first one as possible
slider = [0, 0, 0, 0, 0, 0]

# Slider to keep track of the image frames as corresponding to the original slider
image_slider = [0, 0, 0, 0, 0, 0]

# Defaults the skip index to -1 so as to not create an infinite loop
skip_index = -1

while(True):
	# Prints every 1000 iterations the current iteration
	if not index % 1000:
		print(f"AT ITERATION {index}")

	# If the skip index is greater than 0, reset the sliders and increase the skip index
	if 0 <= skip_index <= len(slider):
		# slides the video forward
		ret, frame = mario_video.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# increase the index
		skip_index += 1
		index += 1

		slider = [0, 0, 0, 0, 0, 0, 0]
		image_slider = [0, 0, 0, 0, 0, 0, 0]
		continue

	# Read the current frame into greyscale
	ret, frame = mario_video.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Add new items to the image slider
	image_slider.pop(0)
	image_slider.append(gray)

	# Get a new scanner object
	scanner = TemplateScanner(["MarioFilter.png",], [gray],
	                          "JumpingTests")

	# Get the export of the scanner
	export = scanner.scan()

	# Slide the slider and get the average
	slider.pop(0)
	slider.append(1 if export[0] else 0)
	average = sum(slider) / len(slider)

	# If the average value is greater than the threshold it's pretty likely there is a jump happening
	if average >= .5:
		cv2.imshow("frame", gray)

		# Get the index of the first positive jump frame and plot it
		index_of_positive = [index for index, value in enumerate(slider) if value == 1][0]
		scanner.plot_template_match(image_slider[index_of_positive], scanner.cur_results, index=index)

		skip_index = 0

	if cv2.waitKey(1) & 0xFF == ord('q'): break

	index += 1

# When everything done, release the capture
mario_video.release()
cv2.destroyAllWindows()
