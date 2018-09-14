"""A file for scanning a video of mario gameplay for jumping
Author: Matthew Byrd
Date created: 8/31/2018
Date last modified: 9/6/2018
"""
import cv2
from TemplateScanner import TemplateScanner

mario_video = cv2.VideoCapture("Sources/SuperMarioBros.mp4")

index = 0

# Slider as to not get all frames of a single jump, instead only getting as close to the first one as possible
slider = [0, 0, 0, 0, 0, 0]

# Slider to keep track of the image frames as corresponding to the original slider
image_slider = [0, 0, 0, 0, 0, 0]

# Defaults the skip index to -1 so as to not create an infinite loop
skip_index = -1

scanner = TemplateScanner(templates=["MarioFilter.png", "MarioFireJump.png"])

while(True):

	# Debugging
	try:

		# Prints the iteration count
		print(index)

		# If the skip index is greater than 0, reset the sliders and increase the skip index
		if 0 <= skip_index <= len(slider):
			# slides the video forward
			ret, frame = mario_video.read()
			gray = frame # cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			# increase the index
			skip_index += 1
			index += 1

			slider = [0, 0, 0, 0, 0, 0, 0]
			image_slider = [0, 0, 0, 0, 0, 0, 0]

			if cv2.waitKey(1) & 0xFF == ord('q'): break
			continue

		# Read the current frame into greyscale
		ret, frame = mario_video.read()

		gray = frame  # cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# Add new items to the image slider
		image_slider.pop(0)
		image_slider.append(gray)

		# Get the export of the scanner
		export = scanner.scan([gray])

		# Slide the slider and get the average
		slider.pop(0)
		slider.append(1 if export[0] else 0)
		average = sum(slider) / len(slider)

		# If the average value is greater than the threshold it's pretty likely there is a jump happening
		if average >= .5:
			cv2.imshow("frame", gray)

			# Get the index of the first positive jump frame and plot it
			index_of_positive = [index for index, value in enumerate(slider) if value == 1][0]
			scanner.scan([image_slider[index_of_positive]])
			scanner.plot_template_match(image_slider[index_of_positive], scanner.cur_results, index=index)

			skip_index = 0

		if cv2.waitKey(1) & 0xFF == ord('q'): break

		index += 1
	except cv2.error as e:
		print(f"ERROR {e}")
		print(f"This is the list of positives {slider}")
		print(f"This is the list of image pointers {image_slider}")
		print(f"This is the index {index}")
		break

# When everything done, release the capture
mario_video.release()
cv2.destroyAllWindows()
