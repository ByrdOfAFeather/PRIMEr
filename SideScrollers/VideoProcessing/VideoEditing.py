"""Code for editing a video
Author: Matthew Byrd
Date created: 9/28/2018
Date last modified: 9/28/2018
"""

from TemplateScannersThreaded import VideoScanner
from threading import Thread
from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips
import datetime


def get_timestamps():
	class JumpThread(Thread):
		def __init__(self):
			Thread.__init__(self)
			self.output = []

		def run(self):
			jump_finder = VideoScanner(templates=["MegaManJumping.png"])

			jump_finder = jump_finder.thread_scanners("Sources/mmlevel1.mp4")
			for threads in jump_finder:
				threads.join()

			for jump_times in jump_finder:
				self.output.extend(jump_times.output)

	class RunThread(Thread):
		def __init__(self):
			Thread.__init__(self)
			self.output = []

		def run(self):
			run_finder = VideoScanner(templates=["MegaManMoving.png"])

			run_finder = run_finder.thread_scanners("Sources/mmlevel1.mp4")
			for threads in run_finder:
				threads.join()

			for run_times in run_finder:
				print(run_times)
				self.output.extend(run_times.output)

	tester1 = JumpThread()
	tester2 = RunThread()

	print("Running Jumper Thread")
	tester1.start()
	print("Running Runner Thread")
	tester2.start()

	tester1.join()
	tester2.join()

	jumps = [f"j{j}" for j in tester1.output]
	runs = [f"r{r}" for r in tester2.output]
	jumps.extend(runs)
	jumps.sort(key=lambda x: x.strip("j").strip("r"))
	return jumps


def find_index(index_start, number_skipped, corpus, search_term):
	for indexer, i in enumerate(corpus[index_start:][number_skipped:]):
		if search_term in i:
			return indexer + number_skipped + index_start
	return -1


timestamps = get_timestamps()
text_base = VideoFileClip("JumpOrMove.mp4")
org_video = VideoFileClip("Sources/mmlevel1.mp4")

cur_type = None
refresh_type = True
choice_list = {}
index = 0

ARBITRARY_SKIP = 10

while index < len(timestamps):
	cur_type = 'j' if 'j' in timestamps[index] else 'r'
	next_type = 'j' if 'j' in timestamps[index + 1] else 'r'

	if cur_type == 'j' and next_type == 'r':
		direct_next_run = timestamps[index + 1]
		a_few_skipped_run = find_index(index, ARBITRARY_SKIP, timestamps, 'r')
		if a_few_skipped_run == -1: break
		choice_list[timestamps[index]] = (timestamps[a_few_skipped_run], direct_next_run)
		index = a_few_skipped_run

	elif cur_type == "j" and next_type == "j": pass

	elif cur_type == "r" and next_type == "j":
		direct_next_jump = timestamps[index + 1]
		a_few_skipped_jump = find_index(index, ARBITRARY_SKIP, timestamps, 'r')
		if a_few_skipped_jump == -1: break
		choice_list[timestamps[index]] = (timestamps[a_few_skipped_jump], direct_next_jump)
		index = a_few_skipped_jump

	elif cur_type == "r" and next_type == "r":
		pass

	index += 1

last_end = 0
edit_list = []
print(choice_list)
print("Here")
text_base = text_base.subclip(0, 3)
for index, items_at_index in enumerate(choice_list.items()):

	print("But not here?")
	starts = items_at_index[0]
	edits = items_at_index[1][0]
	print(starts, edits)
	inital_cut = org_video.subclip(t_start=last_end, t_end=starts)
	edit_list.append(inital_cut)
	edit_list.append(text_base)

	try:
		last_end = list(choice_list.keys())[index + 1]
	except IndexError:
		break

	choice_cut = org_video.subclip(t_start=edits,
	                               t_end=list(choice_list.keys())[index + 1])
	edit_list.append(choice_cut)

print(edit_list)
final = concatenate_videoclips(edit_list, method="compose")
final.write_videofile("outputmmtest1.mp4")

